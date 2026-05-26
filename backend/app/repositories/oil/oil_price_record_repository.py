import operator as comparison
from datetime import date
from uuid import UUID

from sqlalchemy import Row, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.oil.oil_price_record import OilPriceRecord
from app.database.models.oil.oil_series import OilSeries
from app.schemas.oil.filters import OilPriceRecordFilters

# (filter field name on OilPriceRecordFilters, ORM column, comparison op).
# A single table defines every optional filter. Comparisons are only built
# when the filter's value is not None — SQLAlchemy 2.x rejects building
# `column == None` outside an explicit .is_(None) call.
FILTER_RULES = (
    ("oil_series_id", OilPriceRecord.oil_series_id, comparison.eq),
    ("dataset_version_id", OilPriceRecord.dataset_version_id, comparison.eq),
    ("date_from", OilPriceRecord.period, comparison.ge),
    ("date_to", OilPriceRecord.period, comparison.le),
    ("duoarea", OilSeries.duoarea, comparison.eq),
    ("product", OilSeries.product, comparison.eq),
    ("process", OilSeries.process, comparison.eq),
    ("units", OilSeries.units, comparison.eq),
)

SERIES_JOIN_FIELDS = ("duoarea", "product", "process", "units")


class OilPriceRecordRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _needs_series_join(self, filters: OilPriceRecordFilters) -> bool:
        return any(getattr(filters, field) is not None for field in SERIES_JOIN_FIELDS)

    def _active_conditions(self, filters: OilPriceRecordFilters) -> list:
        active = []
        for field_name, column, operator_fn in FILTER_RULES:
            value = getattr(filters, field_name)
            if value is None:
                continue
            active.append(operator_fn(column, value))
        return active

    def _apply_filters(self, query, filters: OilPriceRecordFilters):
        if self._needs_series_join(filters):
            query = query.join(OilSeries, OilPriceRecord.oil_series_id == OilSeries.id)

        for condition in self._active_conditions(filters):
            query = query.where(condition)

        return query

    async def get_records(self, filters: OilPriceRecordFilters) -> list[OilPriceRecord]:
        query = self._apply_filters(select(OilPriceRecord), filters)
        query = query.order_by(OilPriceRecord.period.asc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_weekly_averages(self, filters: OilPriceRecordFilters) -> list[Row]:
        query = select(
            OilPriceRecord.period,
            func.avg(OilPriceRecord.value).label("average_value"),
            func.count(OilPriceRecord.id).label("series_count"),
        )
        query = self._apply_filters(query, filters)
        query = query.group_by(OilPriceRecord.period).order_by(OilPriceRecord.period.asc())
        result = await self.session.execute(query)
        return list(result.all())

    async def count_matching_series(self, filters: OilPriceRecordFilters) -> int:
        query = select(func.count(func.distinct(OilPriceRecord.oil_series_id)))
        query = self._apply_filters(query, filters)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_existing_periods_for_series(self, oil_series_id: UUID) -> set[date]:
        result = await self.session.execute(
            select(OilPriceRecord.period).where(OilPriceRecord.oil_series_id == oil_series_id)
        )
        return set(result.scalars().all())

    async def bulk_create(self, records: list[OilPriceRecord]) -> None:
        self.session.add_all(records)
        await self.session.flush()
