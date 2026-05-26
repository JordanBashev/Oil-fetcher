from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import TYPE_CHECKING

from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.forecasts.forecast_point import ForecastPoint

FORECAST_MODEL_MAX_LENGTH = 64
ERROR_MESSAGE_MAX_LENGTH = 1024
UNITS_MAX_LENGTH = 64


class ForecastStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class ForecastJob(Base):
    __tablename__ = "forecast_jobs"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[ForecastStatus] = mapped_column(SQLEnum(ForecastStatus), nullable=False, default=ForecastStatus.PENDING)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(ERROR_MESSAGE_MAX_LENGTH), nullable=True)

    dataset_version_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("dataset_versions.id", ondelete="RESTRICT"), nullable=False, index=True)
    forecast_model: Mapped[str] = mapped_column(String(FORECAST_MODEL_MAX_LENGTH), nullable=False)
    history_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    horizon_weeks: Mapped[int] = mapped_column(Integer, nullable=False)

    oil_series_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("oil_series.id", ondelete="RESTRICT"), nullable=True)
    units: Mapped[str | None] = mapped_column(String(UNITS_MAX_LENGTH), nullable=True)

    points: Mapped[list[ForecastPoint]] = relationship(back_populates="forecast_job", cascade="all, delete-orphan")
