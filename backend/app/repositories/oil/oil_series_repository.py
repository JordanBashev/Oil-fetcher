from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.oil.oil_price_record import OilPriceRecord
from app.database.models.oil.oil_series import OilSeries


class OilSeriesRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self) -> list[OilSeries]:
        result = await self.session.execute(
            select(OilSeries)
            .where(OilSeries.id.in_(select(OilPriceRecord.oil_series_id).distinct()))
            .order_by(OilSeries.series.asc())
        )
        return list(result.scalars().all())

    async def get_distinct_units(self) -> list[str]:
        result = await self.session.execute(
            select(OilSeries.units)
            .where(OilSeries.id.in_(select(OilPriceRecord.oil_series_id).distinct()))
            .distinct()
            .order_by(OilSeries.units.asc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, oil_series_id: UUID) -> OilSeries | None:
        result = await self.session.execute(
            select(OilSeries).where(OilSeries.id == oil_series_id)
        )
        return result.scalar_one_or_none()

    async def get_by_series_code(self, series_code: str) -> OilSeries | None:
        result = await self.session.execute(
            select(OilSeries).where(OilSeries.series == series_code)
        )
        return result.scalar_one_or_none()

    async def create(self, oil_series: OilSeries) -> OilSeries:
        self.session.add(oil_series)
        await self.session.flush()
        return oil_series

    async def get_or_create(self, oil_series: OilSeries) -> OilSeries:
        existing = await self.get_by_series_code(oil_series.series)
        if existing is not None:
            return existing
        return await self.create(oil_series)
