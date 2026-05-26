from uuid import UUID

from app.database.models.oil.dataset_version import DatasetVersion
from app.repositories.oil.dataset_version_repository import DatasetVersionRepository


class DatasetVersionService:
    def __init__(self, dataset_version_repository: DatasetVersionRepository) -> None:
        self.dataset_version_repository = dataset_version_repository

    async def get_latest(self) -> DatasetVersion | None:
        return await self.dataset_version_repository.get_latest()

    async def get_by_id(self, version_id: UUID) -> DatasetVersion | None:
        return await self.dataset_version_repository.get_by_id(version_id)

    async def get_by_hash(self, dataset_hash: str) -> DatasetVersion | None:
        return await self.dataset_version_repository.get_by_hash(dataset_hash)

    async def get_all(self) -> list[DatasetVersion]:
        return await self.dataset_version_repository.get_all()

    async def create(self, dataset_version: DatasetVersion) -> DatasetVersion:
        return await self.dataset_version_repository.create(dataset_version)
