from uuid import UUID

from sqlalchemy import inspect as sqlalchemy_inspect

from app.database.models.forecasts.forecast_job import ForecastJob
from app.database.models.forecasts.forecast_point import ForecastPoint
from app.schemas.forecasts.responses import ForecastJobResponse, ForecastPointResponse


def build_forecast_response(
    forecast_job: ForecastJob,
    points: list[ForecastPoint],
    latest_dataset_version_id: UUID | None,
) -> ForecastJobResponse:
    """Assemble a ForecastJobResponse from its DB pieces."""
    column_keys = {column.key for column in sqlalchemy_inspect(ForecastJob).mapper.column_attrs}
    column_values = {key: getattr(forecast_job, key) for key in column_keys}

    is_based_on_latest_data = (
        latest_dataset_version_id is not None
        and latest_dataset_version_id == forecast_job.dataset_version_id
    )
    point_responses = [ForecastPointResponse.model_validate(point) for point in points]

    return ForecastJobResponse(
        **column_values,
        is_based_on_latest_data=is_based_on_latest_data,
        points=point_responses,
    )
