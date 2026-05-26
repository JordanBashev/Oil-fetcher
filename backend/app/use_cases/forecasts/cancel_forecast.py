from uuid import UUID

from app.database.models.forecasts.forecast_job import ForecastStatus
from app.database.transaction import Transaction
from app.schemas.forecasts.responses import ForecastJobResponse
from app.services.forecasts.forecast_job_service import ForecastJobService
from app.services.forecasts.forecast_point_service import ForecastPointService
from app.services.oil.dataset_version_service import DatasetVersionService
from app.use_cases.forecasts._owner_check import get_user_owned_job
from app.use_cases.forecasts._response_builder import build_forecast_response
from app.utils.errors.http_errors import FORECAST_NOT_CANCELABLE, http_error


class CancelForecastUseCase:
    def __init__(
        self,
        transaction: Transaction,
        forecast_job_service: ForecastJobService,
        forecast_point_service: ForecastPointService,
        dataset_version_service: DatasetVersionService,
    ) -> None:
        self.transaction = transaction
        self.forecast_job_service = forecast_job_service
        self.forecast_point_service = forecast_point_service
        self.dataset_version_service = dataset_version_service

    async def execute(self, forecast_job_id: UUID, user_id: UUID) -> ForecastJobResponse:
        forecast_job = await get_user_owned_job(self.forecast_job_service, forecast_job_id, user_id)

        if forecast_job.status != ForecastStatus.PENDING:
            raise http_error(FORECAST_NOT_CANCELABLE)

        async with self.transaction:
            forecast_job.status = ForecastStatus.CANCELED
            await self.forecast_job_service.update(forecast_job)

        latest_version = await self.dataset_version_service.get_latest()
        latest_version_id = latest_version.id if latest_version is not None else None
        return build_forecast_response(forecast_job, points=[], latest_dataset_version_id=latest_version_id)
