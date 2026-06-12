"""Sentiment engine — calculates positive/negative sentiment from reviews."""
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.review import Review


def calculate_sentiment(db: Session, game_id: int) -> dict:
    """Calculate sentiment scores for a game from its reviews.

    Returns:
        {
            "positive_pct": float (0-100),
            "negative_pct": float (0-100),
            "total_reviews": int,
            "sentiment_score": int (0-100),
        }
    """
    total = db.query(func.count(Review.id)).filter(Review.game_id == game_id).scalar() or 0
    if total == 0:
        return {
            "positive_pct": 50.0,
            "negative_pct": 50.0,
            "total_reviews": 0,
            "sentiment_score": 50,
        }
    positive = db.query(func.count(Review.id)).filter(
        Review.game_id == game_id, Review.recommended == True
    ).scalar() or 0
    negative = total - positive
    positive_pct = (positive / total) * 100
    negative_pct = (negative / total) * 100
    sentiment_score = round(positive_pct)
    return {
        "positive_pct": round(positive_pct, 1),
        "negative_pct": round(negative_pct, 1),
        "total_reviews": total,
        "sentiment_score": sentiment_score,
    }
