from uuid import UUID

from app.schemas.oil.filters import OilPriceRecordFilters
from app.schemas.oil.responses import OilPricePoint, OilPriceSeries, OilPricesResponse
from app.services.oil.oil_price_record_service import OilPriceRecordService
from app.services.oil.oil_series_service import OilSeriesService
from app.utils.global_messages import AGGREGATE_DESCRIPTION_TEMPLATE, AGGREGATE_SERIES_CODE


class GetOilPricesUseCase:
    def __init__(
        self,
        oil_price_record_service: OilPriceRecordService,
        oil_series_service: OilSeriesService,
    ) -> None:
        self.oil_price_record_service = oil_price_record_service
        self.oil_series_service = oil_series_service

    async def execute(self, filters: OilPriceRecordFilters) -> OilPricesResponse:
        matched_series_count = await self.oil_price_record_service.count_matching_series(filters)
        if filters.oil_series_id is None:
            return await self._build_aggregated_response(filters, matched_series_count)
        return await self._build_per_series_response(filters, matched_series_count)

    async def _build_aggregated_response(
        self,
        filters: OilPriceRecordFilters,
        matched_series_count: int,
    ) -> OilPricesResponse:
        weekly_averages = await self.oil_price_record_service.get_weekly_averages(filters)
        points = [
            OilPricePoint(period=row.period, value=row.average_value)
            for row in weekly_averages
        ]
        aggregated_series = OilPriceSeries(
            series_code=AGGREGATE_SERIES_CODE,
            series_description=AGGREGATE_DESCRIPTION_TEMPLATE.format(count=matched_series_count),
            points=points,
        )
        return OilPricesResponse(
            is_aggregated=True,
            matched_series_count=matched_series_count,
            date_from=filters.date_from,
            date_to=filters.date_to,
            unit_label=filters.units,
            series=[aggregated_series],
        )

    async def _build_per_series_response(
        self,
        filters: OilPriceRecordFilters,
        matched_series_count: int,
    ) -> OilPricesResponse:
        per_series_filters = filters.model_copy(update={"units": None})
        records = await self.oil_price_record_service.get_records(per_series_filters)
        points_by_series: dict[UUID, list[OilPricePoint]] = {}
        for record in records:
            series_points = points_by_series.setdefault(record.oil_series_id, [])
            series_points.append(OilPricePoint(period=record.period, value=record.value))

        unit_label: str | None = None
        series_list = []
        for oil_series_id, points in points_by_series.items():
            oil_series = await self.oil_series_service.get_by_id(oil_series_id)
            unit_label = oil_series.units
            series_list.append(
                OilPriceSeries(
                    series_code=oil_series.series,
                    series_description=oil_series.series_description,
                    points=points,
                )
            )

        return OilPricesResponse(
            is_aggregated=False,
            matched_series_count=matched_series_count,
            date_from=filters.date_from,
            date_to=filters.date_to,
            unit_label=unit_label,
            series=series_list,
        )
