"""Health score algorithm — configurable weights, per-game scoring."""
from datetime import datetime
from sqlalchemy.orm import Session

from src.models.game import Game
from src.models.health_score import HealthScore
from src.models.issue_report import IssueReport
from src.services.sentiment import calculate_sentiment
from src.services.retention import calculate_retention

DEFAULT_WEIGHTS = {
    "sentiment": 0.45,
    "stability": 0.25,
    "retention": 0.20,
    "deck": 0.10,
}


def calculate_deck_score(db: Session, game_id: int) -> int:
    """Calculate deck/playability score (0-100) from controller + linux support."""
    from src.models.game import Game
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game or not game.steam_deck_status:
        return 50  # neutral if unknown
    status = game.steam_deck_status.lower()
    return {"verified": 100, "playable": 75, "unknown": 50, "unsupported": 25}.get(status, 50)


def calculate_stability(db: Session, game_id: int) -> int:
    """Derive stability score (0-100) from issue reports.

    More issues = lower stability. Returns 75 if no reviews.
    """
    issue_counts = db.query(IssueReport).filter(IssueReport.game_id == game_id).all()
    if not issue_counts:
        return 75
    total_issues = len(issue_counts)
    from src.models.review import Review
    total_reviews = db.query(Review).filter(Review.game_id == game_id).count()
    if total_reviews == 0:
        return 75
    issue_ratio = total_issues / total_reviews
    stability = max(0, min(100, round(100 - (issue_ratio * 200))))
    return stability


def get_recommendation(score: int) -> str:
    """Map health score to recommendation string."""
    if score >= 80:
        return "BUY NOW"
    elif score >= 60:
        return "PLAYABLE"
    elif score >= 40:
        return "WAIT FOR PATCHES"
    else:
        return "AVOID FOR NOW"


def calculate_health_score(
    db: Session,
    game_id: int,
    weights: dict | None = None,
) -> dict:
    """Calculate full health score for a game.

    Returns dict with all components and the final score.
    """
    w = weights or DEFAULT_WEIGHTS
    sentiment_data = calculate_sentiment(db, game_id)
    sentiment = sentiment_data["sentiment_score"]
    stability = calculate_stability(db, game_id)
    retention_data = calculate_retention(db, game_id)
    retention = retention_data.get("retention_30d") or 75
    retention = max(0, min(100, round(retention)))
    deck = calculate_deck_score(db, game_id)
    score = round(
        sentiment * w["sentiment"]
        + stability * w["stability"]
        + retention * w["retention"]
        + deck * w["deck"]
    )
    score = max(0, min(100, score))
    recommendation = get_recommendation(score)
    return {
        "game_id": game_id,
        "score": score,
        "sentiment": sentiment,
        "stability": stability,
        "retention": retention,
        "deck": deck,
        "recommendation": recommendation,
    }


def save_health_score(db: Session, game_id: int, weights: dict | None = None) -> HealthScore:
    """Calculate and persist a health score snapshot."""
    data = calculate_health_score(db, game_id, weights)
    hs = HealthScore(
        game_id=game_id,
        score=data["score"],
        sentiment=data["sentiment"],
        stability=data["stability"],
        retention=data["retention"],
        developer_support=0,
        recommendation=data["recommendation"],
        created_at=datetime.now(),
    )
    db.add(hs)
    db.commit()
    return hs
