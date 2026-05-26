from datetime import date
from uuid import UUID

from sqlalchemy import Row

from app.database.models.oil.oil_price_record import OilPriceRecord
from app.repositories.oil.oil_price_record_repository import OilPriceRecordRepository
from app.schemas.oil.filters import OilPriceRecordFilters


class OilPriceRecordService:
    def __init__(self, oil_price_record_repository: OilPriceRecordRepository) -> None:
        self.oil_price_record_repository = oil_price_record_repository

    async def get_records(self, filters: OilPriceRecordFilters) -> list[OilPriceRecord]:
        return await self.oil_price_record_repository.get_records(filters)

    async def get_weekly_averages(self, filters: OilPriceRecordFilters) -> list[Row]:
        return await self.oil_price_record_repository.get_weekly_averages(filters)

    async def count_matching_series(self, filters: OilPriceRecordFilters) -> int:
        return await self.oil_price_record_repository.count_matching_series(filters)

    async def get_existing_periods_for_series(self, oil_series_id: UUID) -> set[date]:
        return await self.oil_price_record_repository.get_existing_periods_for_series(oil_series_id)

    async def bulk_create(self, records: list[OilPriceRecord]) -> None:
        await self.oil_price_record_repository.bulk_create(records)
