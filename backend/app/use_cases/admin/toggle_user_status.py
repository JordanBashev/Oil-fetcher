from uuid import UUID

from app.database.transaction import Transaction
from app.schemas.users.requests import UserStatusRequest
from app.schemas.users.responses import AdminUserResponse
from app.services.users.user_role_service import UserRoleService
from app.services.users.user_service import UserService
from app.utils.errors.http_errors import USER_NOT_FOUND, http_error


class ToggleUserStatusUseCase:
    def __init__(
        self,
        transaction: Transaction,
        user_service: UserService,
        user_role_service: UserRoleService,
    ) -> None:
        self.transaction = transaction
        self.user_service = user_service
        self.user_role_service = user_role_service

    async def execute(self, user_id: UUID, user_status_request: UserStatusRequest) -> AdminUserResponse:
        user = await self.user_service.get_by_id(user_id)
        if user is None:
            raise http_error(USER_NOT_FOUND)

        async with self.transaction:
            user.is_active = user_status_request.is_active
            updated_user = await self.user_service.update(user)

        role_names = await self.user_role_service.get_role_names(updated_user.id)
        return AdminUserResponse(
            id=updated_user.id,
            email=updated_user.email,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at,
            roles=role_names,
        )
