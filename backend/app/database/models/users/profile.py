from __future__ import annotations

from typing import TYPE_CHECKING

from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.users.user import User

NAME_MAX_LENGTH = 100
BIO_MAX_LENGTH = 1000

class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), default="", nullable=False)
    last_name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), default="", nullable=False)
    bio: Mapped[str] = mapped_column(String(BIO_MAX_LENGTH), default="", nullable=False)

    user: Mapped[User] = relationship(back_populates="profile")
