from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_db
from app.database.transaction import Transaction
from app.dependencies._factories import build_user_services
from app.use_cases.users.get_profile import GetProfileUseCase
from app.use_cases.users.update_profile import UpdateProfileUseCase


def get_profile_use_case(
    session: AsyncSession = Depends(get_db),
) -> GetProfileUseCase:
    return GetProfileUseCase(
        profile_service=build_user_services(session).profiles,
    )


def get_update_profile_use_case(
    session: AsyncSession = Depends(get_db),
) -> UpdateProfileUseCase:
    return UpdateProfileUseCase(
        transaction=Transaction(session),
        profile_service=build_user_services(session).profiles,
    )
