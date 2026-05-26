from __future__ import annotations

from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.oil.oil_price_record import OilPriceRecord

HASH_MAX_LENGTH = 64
SOURCE_MAX_LENGTH = 32


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    hash: Mapped[str] = mapped_column(String(HASH_MAX_LENGTH), unique=True, nullable=False, index=True)
    record_count: Mapped[int] = mapped_column(Integer, nullable=False)
    date_from: Mapped[date] = mapped_column(Date, nullable=False)
    date_to: Mapped[date] = mapped_column(Date, nullable=False)
    source: Mapped[str] = mapped_column(String(SOURCE_MAX_LENGTH), nullable=False)

    records: Mapped[list[OilPriceRecord]] = relationship(back_populates="dataset_version")
