from app.schemas.users.responses import AdminUserResponse
from app.services.users.user_service import UserService


class ListUsersUseCase:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def execute(self) -> list[AdminUserResponse]:
        users = await self.user_service.get_all_with_roles()
        return [
            AdminUserResponse(
                id=user.id,
                email=user.email,
                is_active=user.is_active,
                created_at=user.created_at,
                roles=[user_role.role.name for user_role in user.roles],
            )
            for user in users
        ]
