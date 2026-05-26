from uuid import UUID

from app.database.models.forecasts.forecast_point import ForecastPoint
from app.repositories.forecasts.forecast_point_repository import ForecastPointRepository


class ForecastPointService:
    def __init__(self, forecast_point_repository: ForecastPointRepository) -> None:
        self.forecast_point_repository = forecast_point_repository

    async def get_by_job_id(self, forecast_job_id: UUID) -> list[ForecastPoint]:
        return await self.forecast_point_repository.get_by_job_id(forecast_job_id)

    async def bulk_create(self, points: list[ForecastPoint]) -> None:
        await self.forecast_point_repository.bulk_create(points)
