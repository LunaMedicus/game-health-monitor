import asyncio
import httpx
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from src.models.game import Game

STEAM_API_BASE = "https://store.steampowered.com/api/appdetails"
STEAM_SEARCH_BASE = "https://store.steampowered.com/api/storesearch/"
STEAM_APP_LIST_BASE = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
RATE_LIMIT_DELAY = 0.25  # 4 requests/sec max
MAX_RETRIES = 3


async def search_steam_store(query: str, limit: int = 10) -> list[dict]:
    """Search Steam Store for apps matching a query.

    Steam's official IStoreService app list requires a Web API key. This uses
    the public storesearch endpoint so development can work without keys.
    """
    params = {
        "term": query,
        "l": "english",
        "cc": "us",
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(STEAM_SEARCH_BASE, params=params)
            if resp.status_code != 200:
                return []
            data = resp.json()
            results = data.get("items", [])[:limit]
            return [
                {
                    "steam_app_id": item.get("id"),
                    "name": item.get("name"),
                    "cover_url": item.get("tiny_image"),
                    "price": item.get("price", {}).get("final"),
                }
                for item in results
                if item.get("id") and item.get("name")
            ]
    except (httpx.RequestError, httpx.TimeoutException, ValueError):
        return []


async def fetch_public_app_list() -> list[dict]:
    """Fetch the deprecated public Steam app list.

    Prefer IStoreService/GetAppList with a key for production. This endpoint is
    still useful as a fallback where available, but Steam documents it as unable
    to scale to the full catalog.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(STEAM_APP_LIST_BASE)
            if resp.status_code != 200:
                return []
            data = resp.json()
            return data.get("applist", {}).get("apps", [])
    except (httpx.RequestError, httpx.TimeoutException, ValueError):
        return []


async def fetch_steam_metadata(steam_app_id: int) -> Optional[dict]:
    """Fetch game metadata from Steam Store API for a single app_id."""
    url = f"{STEAM_API_BASE}?appids={steam_app_id}"
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url)
                if resp.status_code == 429:
                    await asyncio.sleep(2 ** (attempt + 1))
                    continue
                if resp.status_code != 200:
                    return None
                data = resp.json()
                game_data = data.get(str(steam_app_id), {})
                if not game_data.get("success"):
                    return None
                return game_data["data"]
        except (httpx.RequestError, httpx.TimeoutException):
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(2 ** (attempt + 1))
            continue
    return None


def parse_release_date(raw: str) -> Optional[date]:
    """Parse Steam date strings into a date object."""
    if not raw:
        return None
    from datetime import datetime
    cleaned = raw.strip()
    for fmt in ("%b %d, %Y", "%d %b, %Y", "%b %Y", "%Y"):
        try:
            parsed = datetime.strptime(cleaned, fmt)
            return parsed.date()
        except ValueError:
            continue
    return None


def upsert_game_from_steam(db: Session, steam_app_id: int, data: dict) -> Game:
    """Create or update a Game from Steam API data."""
    existing = db.query(Game).filter(Game.steam_app_id == steam_app_id).first()

    developers = data.get("developers", [])
    publishers = data.get("publishers", [])
    genres = [g.get("description") for g in data.get("genres", []) if g.get("description")]
    platform_flags = data.get("platforms", {})
    platforms = [name.title() for name, enabled in platform_flags.items() if enabled]
    controller_support = data.get("controller_support")
    deck_status = _derive_deck_status(platform_flags, controller_support)
    release_raw = data.get("release_date", {})
    release_date = None
    if isinstance(release_raw, dict):
        release_date = parse_release_date(release_raw.get("date", ""))
    elif isinstance(release_raw, str):
        release_date = parse_release_date(release_raw)

    update_fields = {
        "name": data.get("name"),
        "developer": ", ".join(developers) if developers else None,
        "publisher": ", ".join(publishers) if publishers else None,
        "release_date": release_date,
        "cover_url": data.get("header_image"),
        "genre": ", ".join(genres) if genres else None,
        "platforms": ", ".join(platforms) if platforms else None,
        "controller_support": controller_support,
        "steam_deck_status": deck_status,
    }

    if existing:
        for field, value in update_fields.items():
            if value is not None:
                setattr(existing, field, value)
        return existing

    game = Game(steam_app_id=steam_app_id, **{k: v for k, v in update_fields.items() if v is not None})
    db.add(game)
    db.flush()
    return game


def _derive_deck_status(platforms: dict, controller_support: str | None) -> str | None:
    """Derive Steam Deck compatibility from platform support and controller data.

    Uses Linux platform + controller_support as a heuristic. This is approximate
    because Valve's official Deck verification includes Proton compatibility even
    for Windows-only games. A more accurate source would be a dedicated Deck API.
    """
    if not platforms:
        return None
    has_linux = platforms.get("linux", False)
    has_controller = controller_support in ("full", "partial")
    if has_linux and has_controller:
        return "verified"
    if has_linux or has_controller:
        return "playable"
    return "unknown"


async def import_games_batch(db: Session, steam_app_ids: list[int]) -> list[Game]:
    """Import multiple games from Steam. Returns list of created/updated games."""
    imported = []
    for app_id in steam_app_ids:
        data = await fetch_steam_metadata(app_id)
        if data:
            game = upsert_game_from_steam(db, app_id, data)
            imported.append(game)
        await asyncio.sleep(RATE_LIMIT_DELAY)
    db.commit()
    return imported


async def import_single_game(db: Session, steam_app_id: int) -> Optional[Game]:
    """Import a single game from Steam by its app_id."""
    data = await fetch_steam_metadata(steam_app_id)
    if not data:
        return None
    game = upsert_game_from_steam(db, steam_app_id, data)
    db.commit()
    return game


async def import_first_search_result(db: Session, query: str) -> Optional[Game]:
    """Search Steam by name and import the first appdetails match."""
    results = await search_steam_store(query, limit=10)
    if not results:
        return None
    normalized_query = query.strip().casefold()
    exact_match = next(
        (
            result for result in results
            if result.get("name", "").strip().casefold() == normalized_query
        ),
        None,
    )
    selected = exact_match or results[0]
    return await import_single_game(db, int(selected["steam_app_id"]))
