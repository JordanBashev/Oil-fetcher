from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_db
from app.database.transaction import Transaction
from app.repositories.forecasts.forecast_job_repository import ForecastJobRepository
from app.repositories.forecasts.forecast_point_repository import ForecastPointRepository
from app.repositories.oil.dataset_version_repository import DatasetVersionRepository
from app.services.forecasts.forecast_job_service import ForecastJobService
from app.services.forecasts.forecast_point_service import ForecastPointService
from app.services.oil.dataset_version_service import DatasetVersionService
from app.use_cases.forecasts.cancel_forecast import CancelForecastUseCase
from app.use_cases.forecasts.create_forecast_job import CreateForecastJobUseCase
from app.use_cases.forecasts.delete_forecast import DeleteForecastUseCase
from app.use_cases.forecasts.get_latest_matching_forecast import GetLatestMatchingForecastUseCase
from app.use_cases.forecasts.get_user_forecast import GetUserForecastUseCase
from app.use_cases.forecasts.list_user_forecasts import ListUserForecastsUseCase


def get_create_forecast_job_use_case(
    session: AsyncSession = Depends(get_db),
) -> CreateForecastJobUseCase:
    return CreateForecastJobUseCase(
        transaction=Transaction(session),
        forecast_job_service=ForecastJobService(ForecastJobRepository(session)),
        dataset_version_service=DatasetVersionService(DatasetVersionRepository(session)),
    )


def get_list_user_forecasts_use_case(
    session: AsyncSession = Depends(get_db),
) -> ListUserForecastsUseCase:
    return ListUserForecastsUseCase(
        forecast_job_service=ForecastJobService(ForecastJobRepository(session)),
        forecast_point_service=ForecastPointService(ForecastPointRepository(session)),
        dataset_version_service=DatasetVersionService(DatasetVersionRepository(session)),
    )


def get_user_forecast_use_case(
    session: AsyncSession = Depends(get_db),
) -> GetUserForecastUseCase:
    return GetUserForecastUseCase(
        forecast_job_service=ForecastJobService(ForecastJobRepository(session)),
        forecast_point_service=ForecastPointService(ForecastPointRepository(session)),
        dataset_version_service=DatasetVersionService(DatasetVersionRepository(session)),
    )


def get_latest_matching_forecast_use_case(
    session: AsyncSession = Depends(get_db),
) -> GetLatestMatchingForecastUseCase:
    return GetLatestMatchingForecastUseCase(
        forecast_job_service=ForecastJobService(ForecastJobRepository(session)),
        forecast_point_service=ForecastPointService(ForecastPointRepository(session)),
        dataset_version_service=DatasetVersionService(DatasetVersionRepository(session)),
    )


def get_cancel_forecast_use_case(
    session: AsyncSession = Depends(get_db),
) -> CancelForecastUseCase:
    return CancelForecastUseCase(
        transaction=Transaction(session),
        forecast_job_service=ForecastJobService(ForecastJobRepository(session)),
        forecast_point_service=ForecastPointService(ForecastPointRepository(session)),
        dataset_version_service=DatasetVersionService(DatasetVersionRepository(session)),
    )


def get_delete_forecast_use_case(
    session: AsyncSession = Depends(get_db),
) -> DeleteForecastUseCase:
    return DeleteForecastUseCase(
        transaction=Transaction(session),
        forecast_job_service=ForecastJobService(ForecastJobRepository(session)),
    )
