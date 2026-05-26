from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.database.models.forecasts.forecast_job import ForecastStatus
from app.schemas.common.pagination import PaginationMeta


class ForecastPointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    period: date
    value: float


class ForecastJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    status: ForecastStatus

    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None

    dataset_version_id: UUID
    forecast_model: str
    history_weeks: int
    horizon_weeks: int

    oil_series_id: UUID | None
    units: str | None

    # Both fields are computed/loaded outside the ORM read; defaults let
    # model_validate(orm_job) succeed, then model_copy(update=...) supplies
    # the real values. Without defaults, model_validate would either fail
    # (missing) or lazy-load the SQLAlchemy `points` relationship, which
    # raises MissingGreenlet in async context.
    is_based_on_latest_data: bool = False
    points: list[ForecastPointResponse] = []


class PaginatedForecastsResponse(BaseModel):
    items: list[ForecastJobResponse]
    pagination: PaginationMeta
