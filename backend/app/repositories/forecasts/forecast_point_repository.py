from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.forecasts.forecast_point import ForecastPoint


class ForecastPointRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_job_id(self, forecast_job_id: UUID) -> list[ForecastPoint]:
        result = await self.session.execute(
            select(ForecastPoint)
            .where(ForecastPoint.forecast_job_id == forecast_job_id)
            .order_by(ForecastPoint.period.asc())
        )
        return list(result.scalars().all())

    async def bulk_create(self, points: list[ForecastPoint]) -> None:
        self.session.add_all(points)
        await self.session.flush()
