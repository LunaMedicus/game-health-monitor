"""Import orchestration for turning Steam metadata into usable game data."""
from sqlalchemy.orm import Session

from src.models.game import Game
from src.services.issues import process_reviews_for_issues
from src.services.retention import fetch_current_players, record_player_metric
from src.services.reviews import ingest_reviews
from src.services.scoring import save_health_score


async def hydrate_imported_game(db: Session, game: Game, review_pages: int = 3) -> dict:
    """Populate reviews, issues, player metrics, and a health score for a game."""
    reviews_imported = await ingest_reviews(db, game, max_pages=review_pages)
    issues = process_reviews_for_issues(db, game.id)

    current_players = None
    if game.steam_app_id:
        current_players = await fetch_current_players(game.steam_app_id)
        if current_players is not None:
            record_player_metric(db, game.id, current_players, current_players)

    health_score = save_health_score(db, game.id)

    return {
        "reviews_imported": reviews_imported,
        "issues": issues,
        "current_players": current_players,
        "health_score_id": health_score.id,
        "score": health_score.score,
        "recommendation": health_score.recommendation,
    }
