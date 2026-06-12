from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database import get_db
from src.models.game import Game
from src.models.health_score import HealthScore
from src.models.issue_report import IssueReport
from src.models.review import Review
from src.services.steam import (
    import_single_game,
    import_games_batch,
    import_first_search_result,
    search_steam_store,
)
from src.services.scoring import calculate_health_score, save_health_score
from src.services.recommendations import get_game_recommendation
from src.services.import_pipeline import hydrate_imported_game

router = APIRouter()


class ImportRequest(BaseModel):
    steam_app_ids: list[int]


class SearchImportRequest(BaseModel):
    query: str


def game_to_dict(g: Game, hs: HealthScore | None = None) -> dict:
    d = {
        "id": g.id,
        "steam_app_id": g.steam_app_id,
        "igdb_id": g.igdb_id,
        "name": g.name,
        "release_date": str(g.release_date) if g.release_date else None,
        "developer": g.developer,
        "publisher": g.publisher,
        "cover_url": g.cover_url,
        "platforms": g.platforms,
        "genre": g.genre,
        "steam_deck_status": g.steam_deck_status,
        "controller_support": g.controller_support,
    }
    if hs:
        d["health_score"] = hs.score
        d["recommendation"] = hs.recommendation
        d["sentiment"] = hs.sentiment
        d["stability"] = hs.stability
        d["retention_score"] = hs.retention
    return d


@router.get("/games")
def list_games(
    sort: str = Query("name", pattern="^(name|score|worst)$"),
    db: Session = Depends(get_db),
):
    games = db.query(Game).order_by(Game.name).all()
    result = []
    for g in games:
        hs = db.query(HealthScore).filter(HealthScore.game_id == g.id)\
            .order_by(HealthScore.created_at.desc()).first()
        result.append(game_to_dict(g, hs))
    if sort == "score":
        result.sort(key=lambda x: x.get("health_score") or 0, reverse=True)
    elif sort == "worst":
        result.sort(key=lambda x: x.get("health_score") or 0)
    return result


@router.get("/steam/search")
async def search_steam(query: str, limit: int = Query(10, ge=1, le=25)):
    return await search_steam_store(query, limit=limit)


@router.post("/games/import")
async def import_from_steam(req: ImportRequest, db: Session = Depends(get_db)):
    imported = await import_games_batch(db, req.steam_app_ids)
    pipeline = []
    for game in imported:
        pipeline.append(await hydrate_imported_game(db, game))
    return {
        "imported": len(imported),
        "games": [
            game_to_dict(
                g,
                db.query(HealthScore).filter(HealthScore.game_id == g.id)
                .order_by(HealthScore.created_at.desc()).first(),
            )
            for g in imported
        ],
        "pipeline": pipeline,
    }


@router.post("/games/import/search")
async def import_by_search(req: SearchImportRequest, db: Session = Depends(get_db)):
    game = await import_first_search_result(db, req.query)
    if not game:
        return {"error": "Could not find a Steam result"}
    pipeline = await hydrate_imported_game(db, game)
    hs = db.query(HealthScore).filter(HealthScore.game_id == game.id)\
        .order_by(HealthScore.created_at.desc()).first()
    result = game_to_dict(game, hs)
    result["pipeline"] = pipeline
    return result


@router.post("/games/import/{steam_app_id}")
async def import_single(steam_app_id: int, db: Session = Depends(get_db)):
    game = await import_single_game(db, steam_app_id)
    if not game:
        return {"error": "Could not fetch from Steam"}
    pipeline = await hydrate_imported_game(db, game)
    hs = db.query(HealthScore).filter(HealthScore.game_id == game.id)\
        .order_by(HealthScore.created_at.desc()).first()
    result = game_to_dict(game, hs)
    result["pipeline"] = pipeline
    return result


@router.get("/games/{game_id}")
def get_game(game_id: int, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        return {"error": "Game not found"}
    hs = db.query(HealthScore).filter(HealthScore.game_id == game.id)\
        .order_by(HealthScore.created_at.desc()).first()
    return game_to_dict(game, hs)


@router.get("/games/{game_id}/health")
def get_game_health(game_id: int, db: Session = Depends(get_db)):
    scores = db.query(HealthScore).filter(HealthScore.game_id == game_id)\
        .order_by(HealthScore.created_at.asc()).all()
    return [
        {
            "score": s.score,
            "sentiment": s.sentiment,
            "stability": s.stability,
            "retention": s.retention,
            "developer_support": s.developer_support,
            "recommendation": s.recommendation,
            "created_at": str(s.created_at),
        }
        for s in scores
    ]


@router.get("/games/{game_id}/issues")
def get_game_issues(game_id: int, db: Session = Depends(get_db)):
    issues = db.query(IssueReport).filter(IssueReport.game_id == game_id).all()
    counts: dict[str, int] = {}
    summaries: dict[str, list[str]] = {}
    for issue in issues:
        counts[issue.issue_type] = counts.get(issue.issue_type, 0) + 1
        if issue.summary:
            summaries.setdefault(issue.issue_type, [])
            if issue.summary not in summaries[issue.issue_type]:
                summaries[issue.issue_type].append(issue.summary)
    sorted_issues = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    details = []
    for issue_type, count in sorted_issues:
        details.append({
            "type": issue_type,
            "count": count,
            "summaries": summaries.get(issue_type, [])[:5],
        })
    return {
        "game_id": game_id,
        "total_issues": len(issues),
        "issues": dict(sorted_issues),
        "details": details,
    }


@router.get("/games/{game_id}/recommendation")
def get_recommendation_endpoint(game_id: int, db: Session = Depends(get_db)):
    return get_game_recommendation(db, game_id)


@router.post("/games/{game_id}/score")
def recalculate_score(game_id: int, db: Session = Depends(get_db)):
    hs = save_health_score(db, game_id)
    return {
        "game_id": game_id,
        "score": hs.score,
        "recommendation": hs.recommendation,
        "created_at": str(hs.created_at),
    }
