import logging
from datetime import datetime, timezone
from uuid import UUID

from app.database.models.forecasts.forecast_job import ForecastJob, ForecastStatus
from app.database.models.forecasts.forecast_point import ForecastPoint
from app.database.transaction import Transaction
from app.schemas.oil.filters import DEFAULT_OIL_UNIT, OilPriceRecordFilters
from app.services.forecasts.forecast_job_service import ForecastJobService
from app.services.forecasts.forecast_point_service import ForecastPointService
from app.services.oil.oil_price_record_service import OilPriceRecordService
from app.utils.global_messages import EMPTY_HISTORY_MESSAGE
from app.utils.forecasting.dispatcher import FORECAST_FUNCTIONS
from app.utils.forecasting.types import ForecastModelType
from app.utils.logging_setup.messages import (
    FORECAST_JOB_COMPLETED,
    FORECAST_JOB_CRASHED,
    FORECAST_JOB_FAILED,
    FORECAST_JOB_STARTED,
)

logger = logging.getLogger(__name__)

ERROR_MESSAGE_MAX_LENGTH = 1024


class RunForecastJobUseCase:
    def __init__(
        self,
        transaction: Transaction,
        forecast_job_service: ForecastJobService,
        forecast_point_service: ForecastPointService,
        oil_price_record_service: OilPriceRecordService,
    ) -> None:
        self.transaction = transaction
        self.forecast_job_service = forecast_job_service
        self.forecast_point_service = forecast_point_service
        self.oil_price_record_service = oil_price_record_service

    async def execute(self, forecast_job_id: UUID) -> None:
        forecast_job = await self.forecast_job_service.get_by_id(forecast_job_id)
        if forecast_job is None:
            return
        if forecast_job.status != ForecastStatus.PENDING:
            return

        # Phase 1 — flip status so polling clients can observe PROCESSING.
        async with self.transaction:
            forecast_job.status = ForecastStatus.PROCESSING
            forecast_job.started_at = datetime.now(timezone.utc)
            await self.forecast_job_service.update(forecast_job)
        logger.info(
            FORECAST_JOB_STARTED,
            forecast_job.id,
            forecast_job.forecast_model,
            forecast_job.history_weeks,
            forecast_job.horizon_weeks,
        )

        # Phase 2 — history → forecast → points + COMPLETED, atomically.
        try:
            async with self.transaction:
                point_count = await self._run_forecast(forecast_job)
            logger.info(FORECAST_JOB_COMPLETED, forecast_job.id, point_count)
        except RuntimeError as forecast_error:
            logger.warning(FORECAST_JOB_FAILED, forecast_job_id, forecast_error)
            await self._mark_failed(forecast_job_id, str(forecast_error))
        except Exception as unexpected_error:
            logger.error(FORECAST_JOB_CRASHED, forecast_job_id, exc_info=True)
            await self._mark_failed(forecast_job_id, str(unexpected_error))

    async def _run_forecast(self, forecast_job: ForecastJob) -> int:
        history = await self._load_history(forecast_job)
        if len(history) == 0:
            raise RuntimeError(EMPTY_HISTORY_MESSAGE)

        forecast_function = FORECAST_FUNCTIONS[ForecastModelType(forecast_job.forecast_model)]
        future_points = forecast_function(history, forecast_job.horizon_weeks)

        await self.forecast_point_service.bulk_create(
            [
                ForecastPoint(forecast_job_id=forecast_job.id, period=period, value=value)
                for period, value in future_points
            ]
        )

        forecast_job.status = ForecastStatus.COMPLETED
        forecast_job.completed_at = datetime.now(timezone.utc)
        await self.forecast_job_service.update(forecast_job)
        return len(future_points)

    async def _load_history(self, forecast_job: ForecastJob) -> list[tuple]:
        filters = OilPriceRecordFilters(
            dataset_version_id=forecast_job.dataset_version_id,
            oil_series_id=forecast_job.oil_series_id,
            units=None if forecast_job.oil_series_id is not None else (forecast_job.units or DEFAULT_OIL_UNIT),
        )

        if forecast_job.oil_series_id is not None:
            records = await self.oil_price_record_service.get_records(filters)
            history_points = [(record.period, record.value) for record in records]
        else:
            weekly_averages = await self.oil_price_record_service.get_weekly_averages(filters)
            history_points = [(row.period, float(row.average_value)) for row in weekly_averages]

        history_points.sort(key=lambda point: point[0])
        return history_points[-forecast_job.history_weeks:]

    async def _mark_failed(self, forecast_job_id: UUID, error_message: str) -> None:
        forecast_job = await self.forecast_job_service.get_by_id(forecast_job_id)
        if forecast_job is None:
            return
        async with self.transaction:
            forecast_job.status = ForecastStatus.FAILED
            forecast_job.completed_at = datetime.now(timezone.utc)
            forecast_job.error_message = error_message[:ERROR_MESSAGE_MAX_LENGTH]
            await self.forecast_job_service.update(forecast_job)
