from uuid import UUID

from app.schemas.forecasts.responses import ForecastJobResponse
from app.services.forecasts.forecast_job_service import ForecastJobService
from app.services.forecasts.forecast_point_service import ForecastPointService
from app.services.oil.dataset_version_service import DatasetVersionService
from app.use_cases.forecasts._owner_check import get_user_owned_job
from app.use_cases.forecasts._response_builder import build_forecast_response


class GetUserForecastUseCase:
    def __init__(
        self,
        forecast_job_service: ForecastJobService,
        forecast_point_service: ForecastPointService,
        dataset_version_service: DatasetVersionService,
    ) -> None:
        self.forecast_job_service = forecast_job_service
        self.forecast_point_service = forecast_point_service
        self.dataset_version_service = dataset_version_service

    async def execute(self, forecast_job_id: UUID, user_id: UUID) -> ForecastJobResponse:
        forecast_job = await get_user_owned_job(self.forecast_job_service, forecast_job_id, user_id)
        points = await self.forecast_point_service.get_by_job_id(forecast_job.id)

        latest_version = await self.dataset_version_service.get_latest()
        latest_version_id = latest_version.id if latest_version is not None else None

        return build_forecast_response(forecast_job, points, latest_version_id)
