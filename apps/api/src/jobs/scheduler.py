"""Cron job scheduler — runs data pipeline jobs on intervals."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()


def setup_scheduler():
    """Configure and start the job scheduler."""
    scheduler.add_job(
        job_sync_scores,
        CronTrigger(hour="0"),
        id="sync_scores",
        name="Sync health scores daily",
        replace_existing=True,
    )
    scheduler.add_job(
        job_sync_reviews,
        CronTrigger(hour="*/6"),
        id="sync_reviews",
        name="Sync reviews every 6h",
        replace_existing=True,
    )
    scheduler.start()


async def job_sync_scores():
    """Daily: recalculate health scores for all games."""
    from src.database import SessionLocal
    from src.models.game import Game
    from src.services.scoring import save_health_score
    db = SessionLocal()
    try:
        games = db.query(Game).all()
        for game in games:
            save_health_score(db, game.id)
    finally:
        db.close()


async def job_sync_reviews():
    """Every 6 hours: ingest new reviews for tracked games."""
    from src.database import SessionLocal
    from src.models.game import Game
    from src.services.reviews import ingest_reviews
    db = SessionLocal()
    try:
        games = db.query(Game).filter(Game.steam_app_id.isnot(None)).all()
        for game in games:
            await ingest_reviews(db, game, max_pages=2)
    finally:
        db.close()
