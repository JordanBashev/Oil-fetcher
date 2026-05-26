from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_db
from app.repositories.oil.oil_price_record_repository import OilPriceRecordRepository
from app.repositories.oil.oil_series_repository import OilSeriesRepository
from app.services.oil.oil_price_record_service import OilPriceRecordService
from app.services.oil.oil_series_service import OilSeriesService
from app.use_cases.oil.get_oil_prices import GetOilPricesUseCase
from app.use_cases.oil.list_oil_series import ListOilSeriesUseCase
from app.use_cases.oil.list_units import ListUnitsUseCase


def get_list_oil_series_use_case(
    session: AsyncSession = Depends(get_db),
) -> ListOilSeriesUseCase:
    return ListOilSeriesUseCase(
        OilSeriesService(OilSeriesRepository(session)),
    )


def get_list_units_use_case(
    session: AsyncSession = Depends(get_db),
) -> ListUnitsUseCase:
    return ListUnitsUseCase(
        OilSeriesService(OilSeriesRepository(session)),
    )


def get_oil_prices_use_case(
    session: AsyncSession = Depends(get_db),
) -> GetOilPricesUseCase:
    return GetOilPricesUseCase(
        OilPriceRecordService(OilPriceRecordRepository(session)),
        OilSeriesService(OilSeriesRepository(session)),
    )
