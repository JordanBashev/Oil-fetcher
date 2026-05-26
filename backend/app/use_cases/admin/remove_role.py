from uuid import UUID

from app.database.transaction import Transaction
from app.schemas.users.responses import AdminUserResponse
from app.services.users.role_service import RoleService
from app.services.users.user_role_service import UserRoleService
from app.services.users.user_service import UserService
from app.utils.errors.http_errors import ROLE_NOT_ASSIGNED, ROLE_NOT_FOUND, USER_NOT_FOUND, http_error


class RemoveRoleUseCase:
    def __init__(
        self,
        transaction: Transaction,
        user_service: UserService,
        role_service: RoleService,
        user_role_service: UserRoleService,
    ) -> None:
        self.transaction = transaction
        self.user_service = user_service
        self.role_service = role_service
        self.user_role_service = user_role_service

    async def execute(self, user_id: UUID, role_id: UUID) -> AdminUserResponse:
        user = await self.user_service.get_by_id(user_id)
        if user is None:
            raise http_error(USER_NOT_FOUND)

        role = await self.role_service.get_by_id(role_id)
        if role is None:
            raise http_error(ROLE_NOT_FOUND)

        if not await self.user_role_service.has_role(user_id, role_id):
            raise http_error(ROLE_NOT_ASSIGNED)

        async with self.transaction:
            await self.user_role_service.remove_role(user_id, role_id)

        role_names = await self.user_role_service.get_role_names(user_id)
        return AdminUserResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            roles=role_names,
        )
