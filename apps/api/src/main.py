from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.routers import games, admin
from src.jobs.scheduler import setup_scheduler

app = FastAPI(
    title="Game Health Monitor API",
    description="How broken is this game right now?",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router)
app.include_router(admin.router, prefix="/admin", tags=["admin"])


@app.on_event("startup")
def on_startup():
    setup_scheduler()


@app.get("/health")
def health_check():
    return {"status": "ok"}
