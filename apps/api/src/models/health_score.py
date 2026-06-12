from datetime import datetime
from sqlalchemy import Integer, Float, ForeignKey, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class HealthScore(Base):
    __tablename__ = "health_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    sentiment: Mapped[int] = mapped_column(Integer, nullable=False)
    stability: Mapped[int] = mapped_column(Integer, nullable=False)
    retention: Mapped[int] = mapped_column(Integer, nullable=False)
    developer_support: Mapped[int] = mapped_column(Integer, nullable=False)
    recommendation: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    game = relationship("Game", back_populates="health_scores")
