from fastapi import APIRouter, BackgroundTasks, Depends, Request

from app.config import settings
from app.database.models.users.user import User
from app.dependencies.oil import (
    get_list_oil_series_use_case,
    get_list_units_use_case,
    get_oil_prices_use_case,
)
from app.schemas.oil.filters import OilPriceRecordFilters
from app.schemas.oil.requests import FetchMode, OilFetchRequest
from app.schemas.oil.responses import OilPricesResponse, OilSeriesResponse
from app.services.oil.oil_fetch_runner import run_oil_fetch
from app.use_cases.oil.get_oil_prices import GetOilPricesUseCase
from app.use_cases.oil.list_oil_series import ListOilSeriesUseCase
from app.use_cases.oil.list_units import ListUnitsUseCase
from app.utils.auth import get_current_user, require_admin
from app.utils.errors.http_errors import HISTORICAL_FETCH_NOT_ALLOWED, http_error
from app.utils.rate_limit.keys import per_user_key
from app.utils.rate_limit.setup import limiter

router = APIRouter(prefix="/oil", tags=["oil"])

FETCH_ACCEPTED_MESSAGE = "Oil price fetch started"


@router.post("/fetch", status_code=202)
@limiter.limit(lambda: settings.RATE_LIMIT_OIL_FETCH, key_func=per_user_key)
async def fetch_oil_prices(
    request: Request,
    oil_fetch_request: OilFetchRequest,
    background_tasks: BackgroundTasks,
    _: User = Depends(require_admin),
) -> dict:
    if oil_fetch_request.mode == FetchMode.HISTORICAL:
        raise http_error(HISTORICAL_FETCH_NOT_ALLOWED)

    background_tasks.add_task(run_oil_fetch, oil_fetch_request.mode)
    return {"detail": FETCH_ACCEPTED_MESSAGE}


@router.get("/series", response_model=list[OilSeriesResponse])
async def list_oil_series(
    _: User = Depends(get_current_user),
    use_case: ListOilSeriesUseCase = Depends(get_list_oil_series_use_case),
) -> list[OilSeriesResponse]:
    return await use_case.execute()


@router.get("/units", response_model=list[str])
async def list_units(
    _: User = Depends(get_current_user),
    use_case: ListUnitsUseCase = Depends(get_list_units_use_case),
) -> list[str]:
    return await use_case.execute()


@router.get("/prices", response_model=OilPricesResponse)
async def get_oil_prices(
    filters: OilPriceRecordFilters = Depends(),
    _: User = Depends(get_current_user),
    use_case: GetOilPricesUseCase = Depends(get_oil_prices_use_case),
) -> OilPricesResponse:
    return await use_case.execute(filters)
