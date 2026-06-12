from datetime import date
from sqlalchemy import Integer, String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    steam_app_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    igdb_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    developer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    platforms: Mapped[str | None] = mapped_column(String(512), nullable=True)
    genre: Mapped[str | None] = mapped_column(String(255), nullable=True)
    controller_support: Mapped[str | None] = mapped_column(String(50), nullable=True)
    steam_deck_status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    reviews = relationship("Review", back_populates="game")
    player_metrics = relationship("PlayerMetric", back_populates="game")
    health_scores = relationship("HealthScore", back_populates="game")
    issue_reports = relationship("IssueReport", back_populates="game")
    patches = relationship("Patch", back_populates="game")
