from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from uuid import UUID, uuid4

from sqlalchemy import Date, Float, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.forecasts.forecast_job import ForecastJob


class ForecastPoint(Base):
    __tablename__ = "forecast_points"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    forecast_job_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("forecast_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    period: Mapped[date] = mapped_column(Date, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)

    forecast_job: Mapped[ForecastJob] = relationship(back_populates="points")
