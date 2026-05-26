from fastapi import APIRouter, Depends
from uuid import UUID

from app.database.models.users.user import User
from app.dependencies.admin import (
    get_assign_role_use_case,
    get_delete_user_use_case,
    get_list_logs_use_case,
    get_list_roles_use_case,
    get_list_users_use_case,
    get_remove_role_use_case,
    get_toggle_user_status_use_case,
    get_user_detail_use_case,
)
from app.schemas.common.pagination import PaginationParams
from app.schemas.logs.requests import LogQueryFilters
from app.schemas.logs.responses import PaginatedLogsResponse
from app.schemas.users.requests import AssignRoleRequest, UserStatusRequest
from app.schemas.users.responses import AdminUserResponse, RoleResponse
from app.use_cases.admin.assign_role import AssignRoleUseCase
from app.use_cases.admin.delete_user import DeleteUserUseCase
from app.use_cases.admin.get_user import GetUserUseCase
from app.use_cases.admin.list_logs import ListLogsUseCase
from app.use_cases.admin.list_roles import ListRolesUseCase
from app.use_cases.admin.list_users import ListUsersUseCase
from app.use_cases.admin.remove_role import RemoveRoleUseCase
from app.use_cases.admin.toggle_user_status import ToggleUserStatusUseCase
from app.utils.auth import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[AdminUserResponse])
async def list_users(
    _: User = Depends(require_admin),
    use_case: ListUsersUseCase = Depends(get_list_users_use_case),
) -> list[AdminUserResponse]:
    return await use_case.execute()


@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user(
    user_id: UUID,
    _: User = Depends(require_admin),
    use_case: GetUserUseCase = Depends(get_user_detail_use_case),
) -> AdminUserResponse:
    return await use_case.execute(user_id)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    _: User = Depends(require_admin),
    use_case: DeleteUserUseCase = Depends(get_delete_user_use_case),
) -> dict:
    return await use_case.execute(user_id)


@router.patch("/users/{user_id}/status", response_model=AdminUserResponse)
async def toggle_user_status(
    user_id: UUID,
    user_status_request: UserStatusRequest,
    _: User = Depends(require_admin),
    use_case: ToggleUserStatusUseCase = Depends(get_toggle_user_status_use_case),
) -> AdminUserResponse:
    return await use_case.execute(user_id, user_status_request)


@router.post("/users/{user_id}/roles", response_model=AdminUserResponse)
async def assign_role(
    user_id: UUID,
    assign_role_request: AssignRoleRequest,
    _: User = Depends(require_admin),
    use_case: AssignRoleUseCase = Depends(get_assign_role_use_case),
) -> AdminUserResponse:
    return await use_case.execute(user_id, assign_role_request)


@router.delete("/users/{user_id}/roles/{role_id}", response_model=AdminUserResponse)
async def remove_role(
    user_id: UUID,
    role_id: UUID,
    _: User = Depends(require_admin),
    use_case: RemoveRoleUseCase = Depends(get_remove_role_use_case),
) -> AdminUserResponse:
    return await use_case.execute(user_id, role_id)


@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    _: User = Depends(require_admin),
    use_case: ListRolesUseCase = Depends(get_list_roles_use_case),
) -> list[RoleResponse]:
    return await use_case.execute()


@router.get("/logs", response_model=PaginatedLogsResponse)
async def list_logs(
    filters: LogQueryFilters = Depends(),
    pagination: PaginationParams = Depends(),
    _: User = Depends(require_admin),
    use_case: ListLogsUseCase = Depends(get_list_logs_use_case),
) -> PaginatedLogsResponse:
    return await use_case.execute(filters, pagination)
