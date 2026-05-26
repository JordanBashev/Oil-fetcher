from uuid import UUID

from app.database.models.forecasts.forecast_job import ForecastJob, ForecastStatus
from app.database.transaction import Transaction
from app.schemas.forecasts.requests import CreateForecastRequest
from app.schemas.forecasts.responses import ForecastJobResponse
from app.services.forecasts.forecast_job_service import ForecastJobService
from app.services.oil.dataset_version_service import DatasetVersionService
from app.use_cases.forecasts._response_builder import build_forecast_response
from app.utils.errors.http_errors import (
    FORECAST_ALREADY_EXISTS,
    NO_DATASET_AVAILABLE,
    http_error,
)
from app.utils.forecasting.dispatcher import (
    MODEL_HISTORY_WEEKS,
    SYSTEM_FORECAST_HORIZON_WEEKS,
)


class CreateForecastJobUseCase:
    def __init__(
        self,
        transaction: Transaction,
        forecast_job_service: ForecastJobService,
        dataset_version_service: DatasetVersionService,
    ) -> None:
        self.transaction = transaction
        self.forecast_job_service = forecast_job_service
        self.dataset_version_service = dataset_version_service

    async def execute(self, create_forecast_request: CreateForecastRequest, user_id: UUID) -> ForecastJobResponse:
        latest_version = await self.dataset_version_service.get_latest()
        if latest_version is None:
            raise http_error(NO_DATASET_AVAILABLE)

        candidate_job = ForecastJob(
            **create_forecast_request.model_dump(),
            user_id=user_id,
            status=ForecastStatus.PENDING,
            dataset_version_id=latest_version.id,
            history_weeks=MODEL_HISTORY_WEEKS[create_forecast_request.forecast_model],
            horizon_weeks=SYSTEM_FORECAST_HORIZON_WEEKS,
        )

        existing_duplicate = await self.forecast_job_service.find_existing_duplicate(candidate_job)
        if existing_duplicate is not None:
            raise http_error(FORECAST_ALREADY_EXISTS)

        async with self.transaction:
            created_job = await self.forecast_job_service.create(candidate_job)

        return build_forecast_response(created_job, points=[], latest_dataset_version_id=latest_version.id)
