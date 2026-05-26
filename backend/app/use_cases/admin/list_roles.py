from app.schemas.users.responses import RoleResponse
from app.services.users.role_service import RoleService


class ListRolesUseCase:
    def __init__(self, role_service: RoleService) -> None:
        self.role_service = role_service

    async def execute(self) -> list[RoleResponse]:
        roles = await self.role_service.get_all()
        return [RoleResponse.model_validate(role) for role in roles]
