from uuid import UUID

from app.database.models.oil.oil_series import OilSeries
from app.repositories.oil.oil_series_repository import OilSeriesRepository


class OilSeriesService:
    def __init__(self, oil_series_repository: OilSeriesRepository) -> None:
        self.oil_series_repository = oil_series_repository

    async def get_all(self) -> list[OilSeries]:
        return await self.oil_series_repository.get_all()

    async def get_distinct_units(self) -> list[str]:
        return await self.oil_series_repository.get_distinct_units()

    async def get_by_id(self, oil_series_id: UUID) -> OilSeries | None:
        return await self.oil_series_repository.get_by_id(oil_series_id)

    async def get_by_series_code(self, series_code: str) -> OilSeries | None:
        return await self.oil_series_repository.get_by_series_code(series_code)

    async def create(self, oil_series: OilSeries) -> OilSeries:
        return await self.oil_series_repository.create(oil_series)

    async def get_or_create(self, oil_series: OilSeries) -> OilSeries:
        return await self.oil_series_repository.get_or_create(oil_series)
