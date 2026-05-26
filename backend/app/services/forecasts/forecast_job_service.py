from uuid import UUID

from app.database.models.forecasts.forecast_job import ForecastJob
from app.repositories.forecasts.forecast_job_repository import ForecastJobRepository


class ForecastJobService:
    def __init__(self, forecast_job_repository: ForecastJobRepository) -> None:
        self.forecast_job_repository = forecast_job_repository

    async def get_by_id(self, forecast_job_id: UUID) -> ForecastJob | None:
        return await self.forecast_job_repository.get_by_id(forecast_job_id)

    async def find_existing_duplicate(self, candidate_job: ForecastJob) -> ForecastJob | None:
        return await self.forecast_job_repository.find_existing_duplicate(candidate_job)

    async def find_latest_completed_matching(
        self,
        user_id: UUID,
        oil_series_id: UUID | None,
        units: str | None,
    ) -> ForecastJob | None:
        return await self.forecast_job_repository.find_latest_completed_matching(
            user_id, oil_series_id, units
        )

    async def get_user_jobs(self, user_id: UUID, limit: int, offset: int) -> list[ForecastJob]:
        return await self.forecast_job_repository.get_user_jobs(user_id, limit, offset)

    async def count_user_jobs(self, user_id: UUID) -> int:
        return await self.forecast_job_repository.count_user_jobs(user_id)

    async def create(self, forecast_job: ForecastJob) -> ForecastJob:
        return await self.forecast_job_repository.create(forecast_job)

    async def update(self, forecast_job: ForecastJob) -> ForecastJob:
        return await self.forecast_job_repository.update(forecast_job)

    async def delete(self, forecast_job: ForecastJob) -> None:
        await self.forecast_job_repository.delete(forecast_job)
