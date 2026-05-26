from uuid import UUID

from app.database.models.forecasts.forecast_job import ForecastJob
from app.services.forecasts.forecast_job_service import ForecastJobService
from app.utils.errors.http_errors import FORECAST_NOT_FOUND, http_error


async def get_user_owned_job(
    forecast_job_service: ForecastJobService,
    forecast_job_id: UUID,
    user_id: UUID,
) -> ForecastJob:
    """Load a forecast job and verify the requesting user owns it.

    Raises 404 (not 403) on a missing job OR an ownership mismatch so the
    response does not leak which forecast ids exist for other users.
    """
    forecast_job = await forecast_job_service.get_by_id(forecast_job_id)
    if forecast_job is None or forecast_job.user_id != user_id:
        raise http_error(FORECAST_NOT_FOUND)
    return forecast_job
