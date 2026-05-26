from fastapi import APIRouter, BackgroundTasks, Depends, Request
from uuid import UUID

from app.config import settings
from app.database.models.users.user import User
from app.dependencies.forecasts import (
    get_cancel_forecast_use_case,
    get_create_forecast_job_use_case,
    get_delete_forecast_use_case,
    get_latest_matching_forecast_use_case,
    get_list_user_forecasts_use_case,
    get_user_forecast_use_case,
)
from app.schemas.common.pagination import PaginationParams
from app.schemas.forecasts.requests import CreateForecastRequest, ForecastTarget
from app.schemas.forecasts.responses import ForecastJobResponse, PaginatedForecastsResponse
from app.services.forecasts.forecast_runner import run_forecast
from app.use_cases.forecasts.cancel_forecast import CancelForecastUseCase
from app.use_cases.forecasts.create_forecast_job import CreateForecastJobUseCase
from app.use_cases.forecasts.delete_forecast import DeleteForecastUseCase
from app.use_cases.forecasts.get_latest_matching_forecast import GetLatestMatchingForecastUseCase
from app.use_cases.forecasts.get_user_forecast import GetUserForecastUseCase
from app.use_cases.forecasts.list_user_forecasts import ListUserForecastsUseCase
from app.utils.auth import get_current_user
from app.utils.rate_limit.keys import per_user_key
from app.utils.rate_limit.setup import limiter

router = APIRouter(prefix="/forecasts", tags=["forecasts"])


@router.post("", response_model=ForecastJobResponse, status_code=202)
@limiter.limit(lambda: settings.RATE_LIMIT_FORECAST_CREATE, key_func=per_user_key)
async def create_forecast(
    request: Request,
    create_forecast_request: CreateForecastRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    use_case: CreateForecastJobUseCase = Depends(get_create_forecast_job_use_case),
) -> ForecastJobResponse:
    created_forecast = await use_case.execute(create_forecast_request, current_user.id)
    background_tasks.add_task(run_forecast, created_forecast.id)
    return created_forecast


@router.get("", response_model=PaginatedForecastsResponse)
async def list_forecasts(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    use_case: ListUserForecastsUseCase = Depends(get_list_user_forecasts_use_case),
) -> PaginatedForecastsResponse:
    return await use_case.execute(current_user.id, pagination)


@router.get("/latest-matching", response_model=ForecastJobResponse | None)
async def get_latest_matching_forecast(
    target: ForecastTarget = Depends(),
    current_user: User = Depends(get_current_user),
    use_case: GetLatestMatchingForecastUseCase = Depends(get_latest_matching_forecast_use_case),
) -> ForecastJobResponse | None:
    return await use_case.execute(current_user.id, target.oil_series_id, target.units)


@router.get("/{forecast_job_id}", response_model=ForecastJobResponse)
async def get_forecast(
    forecast_job_id: UUID,
    current_user: User = Depends(get_current_user),
    use_case: GetUserForecastUseCase = Depends(get_user_forecast_use_case),
) -> ForecastJobResponse:
    return await use_case.execute(forecast_job_id, current_user.id)


@router.post("/{forecast_job_id}/cancel", response_model=ForecastJobResponse)
async def cancel_forecast(
    forecast_job_id: UUID,
    current_user: User = Depends(get_current_user),
    use_case: CancelForecastUseCase = Depends(get_cancel_forecast_use_case),
) -> ForecastJobResponse:
    return await use_case.execute(forecast_job_id, current_user.id)


@router.delete("/{forecast_job_id}")
async def delete_forecast(
    forecast_job_id: UUID,
    current_user: User = Depends(get_current_user),
    use_case: DeleteForecastUseCase = Depends(get_delete_forecast_use_case),
) -> dict:
    return await use_case.execute(forecast_job_id, current_user.id)
