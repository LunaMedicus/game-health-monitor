"""Scoring recommendation engine — wraps scoring for API use."""
from src.services.scoring import get_recommendation, calculate_health_score


def get_game_recommendation(db, game_id: int) -> dict:
    """Get recommendation for a game."""
    data = calculate_health_score(db, game_id)
    return {
        "recommendation": data["recommendation"],
        "score": data["score"],
        "breakdown": {
            "sentiment": data["sentiment"],
            "stability": data["stability"],
            "retention": data["retention"],
            "developer_support": data["developer_support"],
        },
    }
