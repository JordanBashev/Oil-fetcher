import logging
from uuid import UUID

from fastapi import Cookie, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ACCESS_TOKEN_COOKIE_NAME, ACCESS_TOKEN_TYPE, ADMIN_ROLE
from app.database.base import get_db
from app.database.models.users.user import User
from app.utils.errors.http_errors import ADMIN_REQUIRED, NOT_AUTHENTICATED, http_error
from app.utils.logging_setup.messages import (
    AUTH_ACCESS_DENIED_INVALID_TOKEN,
    AUTH_ACCESS_DENIED_USER_MISSING_OR_INACTIVE,
    AUTH_ADMIN_ACCESS_DENIED,
)
from app.repositories.users.role_repository import RoleRepository
from app.repositories.users.user_repository import UserRepository
from app.repositories.users.user_role_repository import UserRoleRepository
from app.utils.tokens import TokenError, decode_token

logger = logging.getLogger(__name__)


async def get_current_user(
    session: AsyncSession = Depends(get_db),
    access_token: str | None = Cookie(default=None, alias=ACCESS_TOKEN_COOKIE_NAME),
) -> User:
    if access_token is None:
        raise http_error(NOT_AUTHENTICATED)

    try:
        user_id_str = decode_token(access_token, ACCESS_TOKEN_TYPE)
    except TokenError:
        logger.warning(AUTH_ACCESS_DENIED_INVALID_TOKEN)
        raise http_error(NOT_AUTHENTICATED)

    user = await UserRepository(session).get_by_id(UUID(user_id_str))
    if user is None or not user.is_active:
        logger.warning(AUTH_ACCESS_DENIED_USER_MISSING_OR_INACTIVE, user_id_str)
        raise http_error(NOT_AUTHENTICATED)

    return user


async def require_admin(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> User:
    user_roles = await UserRoleRepository(session).get_roles_by_user_id(current_user.id)
    role_ids = [user_role.role_id for user_role in user_roles]

    admin_role = await RoleRepository(session).get_by_name(ADMIN_ROLE)
    if admin_role is None or admin_role.id not in role_ids:
        logger.warning(AUTH_ADMIN_ACCESS_DENIED, current_user.id)
        raise http_error(ADMIN_REQUIRED)

    return current_user
