from datetime import date
from sqlalchemy import Integer, Float, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class PlayerMetric(Base):
    __tablename__ = "player_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), nullable=False)
    current_players: Mapped[int] = mapped_column(Integer, default=0)
    peak_players: Mapped[int] = mapped_column(Integer, default=0)
    retention_30d: Mapped[float | None] = mapped_column(Float, nullable=True)
    retention_90d: Mapped[float | None] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[date] = mapped_column(Date, nullable=False)

    game = relationship("Game", back_populates="player_metrics")
