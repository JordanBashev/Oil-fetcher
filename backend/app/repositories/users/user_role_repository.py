from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.users.user_role import UserRole


class UserRoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_roles_by_user_id(self, user_id: UUID) -> list[UserRole]:
        result = await self.session.execute(select(UserRole).where(UserRole.user_id == user_id))
        return list(result.scalars().all())

    async def assign_role(self, user_role: UserRole) -> UserRole:
        self.session.add(user_role)
        await self.session.flush()
        return user_role

    async def remove_role(self, user_id: UUID, role_id: UUID) -> None:
        await self.session.execute(
            delete(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )
