from datetime import date
from sqlalchemy import Integer, String, Text, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Patch(Base):
    __tablename__ = "patches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), nullable=False)
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    bug_fixes: Mapped[str | None] = mapped_column(Text, nullable=True)
    performance_fixes: Mapped[str | None] = mapped_column(Text, nullable=True)
    server_fixes: Mapped[str | None] = mapped_column(Text, nullable=True)
    released_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    game = relationship("Game", back_populates="patches")
