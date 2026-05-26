from datetime import date, timedelta

from app.database.models.oil.dataset_version import DatasetVersion
from app.database.models.oil.oil_price_record import OilPriceRecord
from app.database.models.oil.oil_series import OilSeries
from app.database.transaction import Transaction
from app.schemas.oil.external import EiaPriceRow
from app.schemas.oil.requests import FetchMode
from app.schemas.oil.responses import OilFetchResultResponse
from app.services.oil.dataset_version_service import DatasetVersionService
from app.services.oil.external.eia_client import EiaClient
from app.services.oil.external.eia_constants import EIA_DATA_SOURCE_NAME, EIA_HISTORY_YEARS
from app.services.oil.oil_price_record_service import OilPriceRecordService
from app.services.oil.oil_series_service import OilSeriesService
from app.utils.dates import current_week_monday
from app.utils.global_messages import (
    FETCH_SKIPPED_DUPLICATE,
    FETCH_SKIPPED_HISTORICAL_EXISTS,
    FETCH_SKIPPED_NO_DATA,
)
from app.utils.hashing import hash_signatures

WEEKS_PER_YEAR = 52
REVISION_WINDOW_WEEKS = 6

SIGNATURE_FIELD_SEPARATOR = "|"


class FetchOilPricesUseCase:
    def __init__(
        self,
        transaction: Transaction,
        eia_client: EiaClient,
        oil_series_service: OilSeriesService,
        oil_price_record_service: OilPriceRecordService,
        dataset_version_service: DatasetVersionService,
    ) -> None:
        self.transaction = transaction
        self.eia_client = eia_client
        self.oil_series_service = oil_series_service
        self.oil_price_record_service = oil_price_record_service
        self.dataset_version_service = dataset_version_service

    async def execute(self, mode: FetchMode) -> OilFetchResultResponse:
        latest_version = await self.dataset_version_service.get_latest()

        # A historical fetch repopulates 5 years and is only meant for an
        # empty database. If data already exists, running it again would
        # duplicate the whole history, so it is refused here.
        if mode == FetchMode.HISTORICAL and latest_version is not None:
            return OilFetchResultResponse(
                created_version=False,
                dataset_version_id=latest_version.id,
                skipped_reason=FETCH_SKIPPED_HISTORICAL_EXISTS,
            )

        date_from, date_to = self._resolve_date_range(mode)

        fetched_rows = await self.eia_client.fetch_prices(date_from, date_to)
        if len(fetched_rows) == 0:
            return OilFetchResultResponse(created_version=False, skipped_reason=FETCH_SKIPPED_NO_DATA)

        dataset_hash = self._hash_rows(fetched_rows)
        duplicate_version = await self.dataset_version_service.get_by_hash(dataset_hash)
        if duplicate_version is not None:
            return OilFetchResultResponse(
                created_version=False,
                dataset_version_id=duplicate_version.id,
                skipped_reason=FETCH_SKIPPED_DUPLICATE,
            )

        async with self.transaction:
            dataset_version = await self._store_dataset(fetched_rows, dataset_hash, date_from, date_to)

        return OilFetchResultResponse(
            created_version=True,
            dataset_version_id=dataset_version.id,
            record_count=len(fetched_rows),
        )

    def _resolve_date_range(self, mode: FetchMode) -> tuple[date, date]:
        current_monday = current_week_monday()

        if mode == FetchMode.HISTORICAL:
            history_start = current_monday - timedelta(weeks=EIA_HISTORY_YEARS * WEEKS_PER_YEAR)
            return history_start, current_monday

        if mode == FetchMode.WEEKLY_REVISION:
            revision_start = current_monday - timedelta(weeks=REVISION_WINDOW_WEEKS)
            return revision_start, current_monday

        return current_monday, current_monday

    def _hash_rows(self, rows: list[EiaPriceRow]) -> str:
        signatures = [
            SIGNATURE_FIELD_SEPARATOR.join([row.series, row.period.isoformat(), str(row.value)])
            for row in rows
        ]
        return hash_signatures(signatures)

    async def _store_dataset(
        self,
        rows: list[EiaPriceRow],
        dataset_hash: str,
        date_from: date,
        date_to: date,
    ) -> DatasetVersion:
        dataset_version = await self.dataset_version_service.create(
            DatasetVersion(
                hash=dataset_hash,
                record_count=len(rows),
                date_from=date_from,
                date_to=date_to,
                source=EIA_DATA_SOURCE_NAME,
            )
        )

        series_cache = await self._build_series_cache()
        price_records = []
        for row in rows:
            oil_series = await self._resolve_series(row, series_cache)
            price_records.append(
                OilPriceRecord(
                    oil_series_id=oil_series.id,
                    dataset_version_id=dataset_version.id,
                    period=row.period,
                    value=row.value,
                )
            )

        await self.oil_price_record_service.bulk_create(price_records)
        return dataset_version

    async def _build_series_cache(self) -> dict[str, OilSeries]:
        existing_series = await self.oil_series_service.get_all()
        return {oil_series.series: oil_series for oil_series in existing_series}

    async def _resolve_series(
        self,
        row: EiaPriceRow,
        series_cache: dict[str, OilSeries],
    ) -> OilSeries:
        cached_series = series_cache.get(row.series)
        if cached_series is not None:
            return cached_series

        created_series = await self.oil_series_service.create(
            OilSeries(
                series=row.series,
                series_description=row.series_description,
                duoarea=row.duoarea,
                area_name=row.area_name,
                product=row.product,
                product_name=row.product_name,
                process=row.process,
                process_name=row.process_name,
                units=row.units,
            )
        )
        series_cache[row.series] = created_series
        return created_series
