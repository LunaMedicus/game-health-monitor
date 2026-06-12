from datetime import datetime
from sqlalchemy import Integer, String, Text, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    review_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), nullable=False)
    review_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended: Mapped[bool] = mapped_column(Boolean, nullable=False)
    playtime: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    game = relationship("Game", back_populates="reviews")
    issue_reports = relationship("IssueReport", back_populates="review")
