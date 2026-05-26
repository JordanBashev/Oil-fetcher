from uuid import UUID

from app.database import base as database_base
from app.database.transaction import Transaction
from app.repositories.forecasts.forecast_job_repository import ForecastJobRepository
from app.repositories.forecasts.forecast_point_repository import ForecastPointRepository
from app.repositories.oil.oil_price_record_repository import OilPriceRecordRepository
from app.services.forecasts.forecast_job_service import ForecastJobService
from app.services.forecasts.forecast_point_service import ForecastPointService
from app.services.oil.oil_price_record_service import OilPriceRecordService
from app.use_cases.forecasts.run_forecast_job import RunForecastJobUseCase


async def run_forecast(forecast_job_id: UUID) -> None:
    """Open a fresh session and run the forecast worker for the given job id.

    Background tasks and scheduled jobs run outside an HTTP request, so each
    gets its own session. `async_session_maker` is looked up on the module at
    call time so tests can swap it for a test-DB sessionmaker.
    """
    async with database_base.async_session_maker() as session:
        use_case = RunForecastJobUseCase(
            transaction=Transaction(session),
            forecast_job_service=ForecastJobService(ForecastJobRepository(session)),
            forecast_point_service=ForecastPointService(ForecastPointRepository(session)),
            oil_price_record_service=OilPriceRecordService(OilPriceRecordRepository(session)),
        )
        await use_case.execute(forecast_job_id)
