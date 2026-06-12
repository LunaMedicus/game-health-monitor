from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db

router = APIRouter()


@router.get("/status")
def admin_status(db: Session = Depends(get_db)):
    from src.models.game import Game
    from src.models.review import Review
    from src.models.health_score import HealthScore
    return {
        "games_count": db.query(Game).count(),
        "reviews_count": db.query(Review).count(),
        "health_scores_count": db.query(HealthScore).count(),
        "status": "ok",
    }


@router.post("/sync")
def admin_sync(db: Session = Depends(get_db)):
    from src.models.game import Game
    from src.services.scoring import save_health_score
    games = db.query(Game).all()
    scored = 0
    for game in games:
        save_health_score(db, game.id)
        scored += 1
    return {"synced": scored}
