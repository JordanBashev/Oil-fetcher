from app.database import base as database_base
from app.database.transaction import Transaction
from app.repositories.oil.dataset_version_repository import DatasetVersionRepository
from app.repositories.oil.oil_price_record_repository import OilPriceRecordRepository
from app.repositories.oil.oil_series_repository import OilSeriesRepository
from app.schemas.oil.requests import FetchMode
from app.schemas.oil.responses import OilFetchResultResponse
from app.services.oil.dataset_version_service import DatasetVersionService
from app.services.oil.external.eia_client import EiaClient
from app.services.oil.oil_price_record_service import OilPriceRecordService
from app.services.oil.oil_series_service import OilSeriesService
from app.use_cases.oil.fetch_oil_prices import FetchOilPricesUseCase


async def run_oil_fetch(mode: FetchMode) -> OilFetchResultResponse:
    """Open a fresh session and run the oil price fetch in the given mode."""
    async with database_base.async_session_maker() as session:
        use_case = FetchOilPricesUseCase(
            transaction=Transaction(session),
            eia_client=EiaClient(),
            oil_series_service=OilSeriesService(OilSeriesRepository(session)),
            oil_price_record_service=OilPriceRecordService(OilPriceRecordRepository(session)),
            dataset_version_service=DatasetVersionService(DatasetVersionRepository(session)),
        )
        return await use_case.execute(mode)
