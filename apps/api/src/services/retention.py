"""Player retention service — tracks player counts and retention."""
import asyncio
import httpx
from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.game import Game
from src.models.player_metric import PlayerMetric

STEAM_PLAYER_COUNT_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
MAX_RETRIES = 3


async def fetch_current_players(steam_app_id: int) -> Optional[int]:
    """Fetch current player count from Steam."""
    params = {"appid": steam_app_id}
    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(STEAM_PLAYER_COUNT_URL, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("response", {}).get("player_count")
                if resp.status_code == 429:
                    await asyncio.sleep(2 ** (attempt + 1))
                    continue
        except (httpx.RequestError, httpx.TimeoutException):
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(2 ** (attempt + 1))
    return None


def record_player_metric(db: Session, game_id: int, current: int, peak: int) -> PlayerMetric:
    """Record a player metric snapshot for a game."""
    metric = PlayerMetric(
        game_id=game_id,
        current_players=current,
        peak_players=peak,
        recorded_at=date.today(),
    )
    db.add(metric)
    db.commit()
    return metric


def calculate_retention(db: Session, game_id: int) -> dict:
    """Calculate 30-day and 90-day retention from player metrics."""
    today = date.today()
    metrics_30 = db.query(PlayerMetric).filter(
        PlayerMetric.game_id == game_id,
        PlayerMetric.recorded_at >= today - timedelta(days=30),
    ).order_by(PlayerMetric.recorded_at.asc()).all()
    metrics_90 = db.query(PlayerMetric).filter(
        PlayerMetric.game_id == game_id,
        PlayerMetric.recorded_at >= today - timedelta(days=90),
    ).order_by(PlayerMetric.recorded_at.asc()).all()
    retention_30 = None
    retention_90 = None
    if len(metrics_30) >= 2:
        first_30 = metrics_30[0].current_players
        last_30 = metrics_30[-1].current_players
        if first_30 > 0:
            retention_30 = round((last_30 / first_30) * 100, 1)
    if len(metrics_90) >= 2:
        first_90 = metrics_90[0].current_players
        last_90 = metrics_90[-1].current_players
        if first_90 > 0:
            retention_90 = round((last_90 / first_90) * 100, 1)
    return {
        "retention_30d": retention_30,
        "retention_90d": retention_90,
        "data_points_30d": len(metrics_30),
        "data_points_90d": len(metrics_90),
    }
