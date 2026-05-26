from uuid import UUID

from app.database.models.users.user_role import UserRole
from app.repositories.users.role_repository import RoleRepository
from app.repositories.users.user_role_repository import UserRoleRepository


class UserRoleService:
    def __init__(
        self,
        user_role_repository: UserRoleRepository,
        role_repository: RoleRepository,
    ) -> None:
        self.user_role_repository = user_role_repository
        self.role_repository = role_repository

    async def get_roles_by_user_id(self, user_id: UUID) -> list[UserRole]:
        return await self.user_role_repository.get_roles_by_user_id(user_id)

    async def has_role(self, user_id: UUID, role_id: UUID) -> bool:
        existing = await self.user_role_repository.get_roles_by_user_id(user_id)
        return any(user_role.role_id == role_id for user_role in existing)

    async def get_role_names(self, user_id: UUID) -> list[str]:
        user_roles = await self.user_role_repository.get_roles_by_user_id(user_id)
        role_names = []
        for user_role in user_roles:
            role = await self.role_repository.get_by_id(user_role.role_id)
            if role is not None:
                role_names.append(role.name)
        return role_names

    async def assign_role(self, user_role: UserRole) -> UserRole:
        return await self.user_role_repository.assign_role(user_role)

    async def remove_role(self, user_id: UUID, role_id: UUID) -> None:
        await self.user_role_repository.remove_role(user_id, role_id)
