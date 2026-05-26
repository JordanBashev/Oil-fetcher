from uuid import UUID

from app.schemas.common.pagination import PaginationMeta, PaginationParams
from app.schemas.forecasts.responses import PaginatedForecastsResponse
from app.services.forecasts.forecast_job_service import ForecastJobService
from app.services.forecasts.forecast_point_service import ForecastPointService
from app.services.oil.dataset_version_service import DatasetVersionService
from app.use_cases.forecasts._response_builder import build_forecast_response


class ListUserForecastsUseCase:
    def __init__(
        self,
        forecast_job_service: ForecastJobService,
        forecast_point_service: ForecastPointService,
        dataset_version_service: DatasetVersionService,
    ) -> None:
        self.forecast_job_service = forecast_job_service
        self.forecast_point_service = forecast_point_service
        self.dataset_version_service = dataset_version_service

    async def execute(self, user_id: UUID, pagination: PaginationParams) -> PaginatedForecastsResponse:
        forecast_jobs = await self.forecast_job_service.get_user_jobs(
            user_id, pagination.limit, pagination.offset
        )
        total_count = await self.forecast_job_service.count_user_jobs(user_id)

        latest_version = await self.dataset_version_service.get_latest()
        latest_version_id = latest_version.id if latest_version is not None else None

        items = []
        for forecast_job in forecast_jobs:
            points = await self.forecast_point_service.get_by_job_id(forecast_job.id)
            items.append(build_forecast_response(forecast_job, points, latest_version_id))

        return PaginatedForecastsResponse(
            items=items,
            pagination=PaginationMeta.build(total_count, pagination),
        )
