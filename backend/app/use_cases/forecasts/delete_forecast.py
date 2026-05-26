from uuid import UUID

from app.database.transaction import Transaction
from app.services.forecasts.forecast_job_service import ForecastJobService
from app.use_cases.forecasts._owner_check import get_user_owned_job
from app.utils.global_messages import FORECAST_DELETED_MESSAGE


class DeleteForecastUseCase:
    def __init__(
        self,
        transaction: Transaction,
        forecast_job_service: ForecastJobService,
    ) -> None:
        self.transaction = transaction
        self.forecast_job_service = forecast_job_service

    async def execute(self, forecast_job_id: UUID, user_id: UUID) -> dict:
        forecast_job = await get_user_owned_job(self.forecast_job_service, forecast_job_id, user_id)

        async with self.transaction:
            await self.forecast_job_service.delete(forecast_job)

        return {"detail": FORECAST_DELETED_MESSAGE}
