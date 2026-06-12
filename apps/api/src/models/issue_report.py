from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class IssueReport(Base):
    __tablename__ = "issue_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), nullable=False)
    review_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("reviews.id"), nullable=True)
    issue_type: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(default=1.0)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    game = relationship("Game", back_populates="issue_reports")
    review = relationship("Review", back_populates="issue_reports")
