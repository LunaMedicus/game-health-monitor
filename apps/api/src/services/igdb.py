import asyncio
import httpx
from typing import Optional

from src.config import settings

IGDB_API_BASE = "https://api.igdb.com/v4"
RATE_LIMIT_DELAY = 0.3  # IGDB: 4 req/sec
MAX_RETRIES = 3

_token: Optional[str] = None
_token_expiry: float = 0


async def _get_twitch_token() -> Optional[str]:
    """Get Twitch OAuth token for IGDB API access."""
    global _token, _token_expiry
    import time
    if _token and time.time() < _token_expiry:
        return _token
    if not settings.igdb_client_id or not settings.igdb_client_secret:
        return None
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://id.twitch.tv/oauth2/token",
                params={
                    "client_id": settings.igdb_client_id,
                    "client_secret": settings.igdb_client_secret,
                    "grant_type": "client_credentials",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                _token = data["access_token"]
                _token_expiry = time.time() + data.get("expires_in", 3600) - 60
                return _token
    except httpx.RequestError:
        pass
    return None


async def igdb_query(endpoint: str, fields: str, where: str = "") -> list[dict]:
    """Execute a query against the IGDB API."""
    token = await _get_twitch_token()
    if not token:
        return []
    client_id = settings.igdb_client_id
    body = f"fields {fields};"
    if where:
        body += f" where {where};"
    body += " limit 50;"
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{IGDB_API_BASE}/{endpoint}",
                    content=body,
                    headers={
                        "Client-ID": client_id,
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "text/plain",
                    },
                )
                if resp.status_code == 200:
                    return resp.json()
                if resp.status_code == 429:
                    await asyncio.sleep(2 ** (attempt + 1))
                    continue
                return []
        except (httpx.RequestError, httpx.TimeoutException):
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(2 ** (attempt + 1))
    return []


async def search_game_by_name(name: str) -> Optional[dict]:
    """Search IGDB for a game by name, return first match."""
    results = await igdb_query(
        "games",
        "id, name, url, genres.name, platforms.name, franchises.name, cover.url, screenshots.url, first_release_date",
        f'name ~ "{name}"',
    )
    return results[0] if results else None


async def enrich_game_from_igdb(game_name: str) -> Optional[dict]:
    """Fetch enrichment data from IGDB for a game."""
    match = await search_game_by_name(game_name)
    if not match:
        return None
    genres = [g["name"] for g in match.get("genres", [])]
    platforms = [p["name"] for p in match.get("platforms", [])]
    franchises = [f["name"] for f in match.get("franchises", [])]
    cover = match.get("cover", {})
    cover_url = cover.get("url", "").replace("t_thumb", "t_1080p") if cover else None
    screenshots = match.get("screenshots", [])
    screenshot_urls = [s.get("url", "").replace("t_thumb", "t_1080p") for s in screenshots[:5]]
    return {
        "igdb_id": match.get("id"),
        "cover_url": cover_url,
        "platforms": ", ".join(platforms) if platforms else None,
        "genre": ", ".join(genres) if genres else None,
        "franchises": ", ".join(franchises) if franchises else None,
        "screenshot_urls": screenshot_urls,
    }
