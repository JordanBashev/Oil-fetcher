from uuid import UUID

from app.schemas.users.responses import AdminUserResponse
from app.services.users.user_role_service import UserRoleService
from app.services.users.user_service import UserService
from app.utils.errors.http_errors import USER_NOT_FOUND, http_error


class GetUserUseCase:
    def __init__(
        self,
        user_service: UserService,
        user_role_service: UserRoleService,
    ) -> None:
        self.user_service = user_service
        self.user_role_service = user_role_service

    async def execute(self, user_id: UUID) -> AdminUserResponse:
        user = await self.user_service.get_by_id(user_id)
        if user is None:
            raise http_error(USER_NOT_FOUND)

        role_names = await self.user_role_service.get_role_names(user.id)
        return AdminUserResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            roles=role_names,
        )
