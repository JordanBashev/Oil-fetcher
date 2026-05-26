from __future__ import annotations

from typing import TYPE_CHECKING

from uuid import UUID, uuid4

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.users.user_role import UserRole

NAME_MAX_LENGTH = 32


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), unique=True, nullable=False, index=True)

    users: Mapped[list[UserRole]] = relationship(back_populates="role", cascade="all, delete-orphan")
