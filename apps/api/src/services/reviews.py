"""Review ingestion pipeline — fetches Steam reviews for a game."""
import asyncio
import httpx
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from src.models.game import Game
from src.models.review import Review

STEAM_REVIEW_URL = "https://store.steampowered.com/appreviews/{app_id}"
RATE_LIMIT_DELAY = 0.5
MAX_RETRIES = 3


async def fetch_steam_reviews(steam_app_id: int, cursor: str = "*", count: int = 100) -> dict:
    """Fetch a batch of Steam reviews for a given app_id."""
    url = STEAM_REVIEW_URL.format(app_id=steam_app_id)
    params = {
        "json": "1",
        "filter": "recent",
        "language": "all",
        "num_per_page": count,
        "cursor": cursor,
    }
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    return resp.json()
                if resp.status_code == 429:
                    await asyncio.sleep(2 ** (attempt + 1))
                    continue
                return {}
        except (httpx.RequestError, httpx.TimeoutException):
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(2 ** (attempt + 1))
    return {}


def upsert_review(db: Session, game_id: int, review_data: dict) -> Optional[Review]:
    """Create or skip a review if it already exists."""
    review_id = str(review_data.get("recommendationid", ""))
    existing = db.query(Review).filter(Review.review_id == review_id).first()
    if existing:
        return None
    review = Review(
        review_id=review_id,
        game_id=game_id,
        review_text=review_data.get("review", ""),
        recommended=review_data.get("voted_up", True),
        playtime=review_data.get("author", {}).get("playtime_forever", 0) / 60,
        created_at=datetime.fromtimestamp(
            review_data.get("timestamp_created", 0)
        ) if review_data.get("timestamp_created") else None,
    )
    db.add(review)
    return review


async def ingest_reviews(db: Session, game: Game, max_pages: int = 5) -> int:
    """Fetch and store reviews for a game. Returns count of new reviews."""
    if not game.steam_app_id:
        return 0
    total_new = 0
    cursor = "*"
    for _ in range(max_pages):
        data = await fetch_steam_reviews(game.steam_app_id, cursor=cursor)
        reviews = data.get("reviews", [])
        if not reviews:
            break
        for r in reviews:
            result = upsert_review(db, game.id, r)
            if result:
                total_new += 1
        cursor = data.get("cursor", "*")
        if not cursor or cursor == "*":
            break
        await asyncio.sleep(RATE_LIMIT_DELAY)
    db.commit()
    return total_new
