from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_db
from app.database.transaction import Transaction
from app.dependencies._factories import build_user_services
from app.use_cases.auth.login import LoginUseCase
from app.use_cases.auth.refresh import RefreshUseCase
from app.use_cases.auth.register import RegisterUseCase


def get_register_use_case(
    session: AsyncSession = Depends(get_db),
) -> RegisterUseCase:
    services = build_user_services(session)
    return RegisterUseCase(
        transaction=Transaction(session),
        user_service=services.users,
        profile_service=services.profiles,
        role_service=services.roles,
        user_role_service=services.user_roles,
    )


def get_login_use_case(
    session: AsyncSession = Depends(get_db),
) -> LoginUseCase:
    services = build_user_services(session)
    return LoginUseCase(
        user_service=services.users,
        user_role_service=services.user_roles,
    )


def get_refresh_use_case(
    session: AsyncSession = Depends(get_db),
) -> RefreshUseCase:
    services = build_user_services(session)
    return RefreshUseCase(
        user_service=services.users,
        user_role_service=services.user_roles,
    )
