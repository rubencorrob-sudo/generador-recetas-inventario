from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(180), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    servings: Mapped[int | None] = mapped_column(Integer, nullable=True, default=1)
    ingredients: Mapped[list[dict]] = mapped_column(JSON)
    steps: Mapped[list[str]] = mapped_column(JSON)
    missing_ingredients: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True, default=list
    )
    tips: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, default=list)
    nutrition: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, default=list)
    estimated_time: Mapped[str] = mapped_column(String(80))
    difficulty: Mapped[str] = mapped_column(String(40))
    is_favorite: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, default=False
    )
    prompt: Mapped[str] = mapped_column(Text)
    raw_response: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    owner = relationship("User", back_populates="recipes")
    ratings = relationship("Rating", back_populates="recipe", cascade="all, delete-orphan")
