from uuid import UUID

from app.database.models.users.role import Role
from app.repositories.users.role_repository import RoleRepository


class RoleService:
    def __init__(self, role_repository: RoleRepository) -> None:
        self.role_repository = role_repository

    async def get_all(self) -> list[Role]:
        return await self.role_repository.get_all()

    async def get_by_id(self, role_id: UUID) -> Role | None:
        return await self.role_repository.get_by_id(role_id)

    async def get_by_name(self, name: str) -> Role | None:
        return await self.role_repository.get_by_name(name)
