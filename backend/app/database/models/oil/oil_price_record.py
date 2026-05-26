from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from uuid import UUID, uuid4

from sqlalchemy import Date, Float, ForeignKey, Integer, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.oil.oil_series import OilSeries
    from app.database.models.oil.dataset_version import DatasetVersion


class OilPriceRecord(Base):
    __tablename__ = "oil_price_records"
    __table_args__ = (
        UniqueConstraint(
            "oil_series_id",
            "period",
            "dataset_version_id",
            name="uq_oil_price_record_series_period_version",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    oil_series_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("oil_series.id", ondelete="CASCADE"), nullable=False, index=True)
    dataset_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=False, index=True)

    period: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)

    oil_series: Mapped[OilSeries] = relationship(back_populates="price_records")
    dataset_version: Mapped[DatasetVersion] = relationship(back_populates="records")
