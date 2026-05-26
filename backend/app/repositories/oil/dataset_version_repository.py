from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.oil.dataset_version import DatasetVersion


class DatasetVersionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_latest(self) -> DatasetVersion | None:
        result = await self.session.execute(
            select(DatasetVersion).order_by(DatasetVersion.fetched_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, version_id: UUID) -> DatasetVersion | None:
        result = await self.session.execute(
            select(DatasetVersion).where(DatasetVersion.id == version_id)
        )
        return result.scalar_one_or_none()

    async def get_by_hash(self, dataset_hash: str) -> DatasetVersion | None:
        result = await self.session.execute(
            select(DatasetVersion).where(DatasetVersion.hash == dataset_hash)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[DatasetVersion]:
        result = await self.session.execute(
            select(DatasetVersion).order_by(DatasetVersion.fetched_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, dataset_version: DatasetVersion) -> DatasetVersion:
        self.session.add(dataset_version)
        await self.session.flush()
        return dataset_version
