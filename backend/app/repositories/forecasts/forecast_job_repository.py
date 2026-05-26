from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.forecasts.forecast_job import ForecastJob, ForecastStatus

DUPLICATE_BLOCKING_STATUSES = (
    ForecastStatus.PENDING,
    ForecastStatus.PROCESSING,
    ForecastStatus.COMPLETED,
)


class ForecastJobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, forecast_job_id: UUID) -> ForecastJob | None:
        result = await self.session.execute(
            select(ForecastJob).where(ForecastJob.id == forecast_job_id)
        )
        return result.scalar_one_or_none()

    async def find_existing_duplicate(self, candidate_job: ForecastJob) -> ForecastJob | None:
        result = await self.session.execute(
            select(ForecastJob).where(
                ForecastJob.user_id == candidate_job.user_id,
                ForecastJob.forecast_model == candidate_job.forecast_model,
                ForecastJob.dataset_version_id == candidate_job.dataset_version_id,
                ForecastJob.history_weeks == candidate_job.history_weeks,
                ForecastJob.horizon_weeks == candidate_job.horizon_weeks,
                ForecastJob.oil_series_id == candidate_job.oil_series_id,
                ForecastJob.units == candidate_job.units,
                ForecastJob.status.in_(DUPLICATE_BLOCKING_STATUSES),
            )
        )
        return result.scalars().first()

    async def find_latest_completed_matching(
        self,
        user_id: UUID,
        oil_series_id: UUID | None,
        units: str | None,
        forecast_model: str | None = None,
    ) -> ForecastJob | None:
        query = (
            select(ForecastJob)
            .where(
                ForecastJob.user_id == user_id,
                ForecastJob.status == ForecastStatus.COMPLETED,
                ForecastJob.oil_series_id == oil_series_id,
                ForecastJob.units == units,
            )
            .order_by(ForecastJob.created_at.desc())
            .limit(1)
        )
        if forecast_model is not None:
            query = query.where(ForecastJob.forecast_model == forecast_model)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_user_jobs(self, user_id: UUID, limit: int, offset: int) -> list[ForecastJob]:
        result = await self.session.execute(
            select(ForecastJob)
            .where(ForecastJob.user_id == user_id)
            .order_by(ForecastJob.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def count_user_jobs(self, user_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(ForecastJob).where(ForecastJob.user_id == user_id)
        )
        return result.scalar_one()

    async def create(self, forecast_job: ForecastJob) -> ForecastJob:
        self.session.add(forecast_job)
        await self.session.flush()
        return forecast_job

    async def update(self, forecast_job: ForecastJob) -> ForecastJob:
        await self.session.flush()
        return forecast_job

    async def delete(self, forecast_job: ForecastJob) -> None:
        await self.session.delete(forecast_job)
        await self.session.flush()
