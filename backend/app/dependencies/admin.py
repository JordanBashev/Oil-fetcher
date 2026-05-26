from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_db
from app.database.transaction import Transaction
from app.dependencies._factories import build_user_services
from app.use_cases.admin.assign_role import AssignRoleUseCase
from app.use_cases.admin.delete_user import DeleteUserUseCase
from app.use_cases.admin.get_user import GetUserUseCase
from app.use_cases.admin.list_logs import ListLogsUseCase
from app.use_cases.admin.list_roles import ListRolesUseCase
from app.use_cases.admin.list_users import ListUsersUseCase
from app.use_cases.admin.remove_role import RemoveRoleUseCase
from app.use_cases.admin.toggle_user_status import ToggleUserStatusUseCase


def get_list_users_use_case(
    session: AsyncSession = Depends(get_db),
) -> ListUsersUseCase:
    return ListUsersUseCase(build_user_services(session).users)


def get_user_detail_use_case(
    session: AsyncSession = Depends(get_db),
) -> GetUserUseCase:
    services = build_user_services(session)
    return GetUserUseCase(services.users, services.user_roles)


def get_delete_user_use_case(
    session: AsyncSession = Depends(get_db),
) -> DeleteUserUseCase:
    return DeleteUserUseCase(
        Transaction(session),
        build_user_services(session).users,
    )


def get_toggle_user_status_use_case(
    session: AsyncSession = Depends(get_db),
) -> ToggleUserStatusUseCase:
    services = build_user_services(session)
    return ToggleUserStatusUseCase(
        Transaction(session),
        services.users,
        services.user_roles,
    )


def get_assign_role_use_case(
    session: AsyncSession = Depends(get_db),
) -> AssignRoleUseCase:
    services = build_user_services(session)
    return AssignRoleUseCase(
        Transaction(session),
        services.users,
        services.roles,
        services.user_roles,
    )


def get_remove_role_use_case(
    session: AsyncSession = Depends(get_db),
) -> RemoveRoleUseCase:
    services = build_user_services(session)
    return RemoveRoleUseCase(
        Transaction(session),
        services.users,
        services.roles,
        services.user_roles,
    )


def get_list_logs_use_case() -> ListLogsUseCase:
    return ListLogsUseCase()


def get_list_roles_use_case(
    session: AsyncSession = Depends(get_db),
) -> ListRolesUseCase:
    return ListRolesUseCase(build_user_services(session).roles)
