import logging
from uuid import UUID

from fastapi.responses import Response

from app.config import ACCESS_TOKEN_COOKIE_NAME, COOKIE_SAMESITE, REFRESH_TOKEN_TYPE, settings
from app.schemas.auth.responses import AuthResponse, AuthUserResponse
from app.services.users.user_role_service import UserRoleService
from app.services.users.user_service import UserService
from app.utils.errors.http_errors import INVALID_REFRESH_TOKEN, http_error
from app.utils.logging_setup.messages import (
    REFRESH_FAILED_INVALID_TOKEN,
    REFRESH_FAILED_MISSING_TOKEN,
    REFRESH_FAILED_USER_MISSING_OR_INACTIVE,
    REFRESH_SUCCESS,
)
from app.utils.tokens import TokenError, create_access_token, decode_token

logger = logging.getLogger(__name__)


class RefreshUseCase:
    def __init__(
        self,
        user_service: UserService,
        user_role_service: UserRoleService,
    ) -> None:
        self.user_service = user_service
        self.user_role_service = user_role_service

    async def execute(self, refresh_token: str | None, response: Response) -> AuthResponse:
        if refresh_token is None:
            logger.warning(REFRESH_FAILED_MISSING_TOKEN)
            raise http_error(INVALID_REFRESH_TOKEN)

        try:
            user_id_str = decode_token(refresh_token, REFRESH_TOKEN_TYPE)
        except TokenError:
            logger.warning(REFRESH_FAILED_INVALID_TOKEN)
            raise http_error(INVALID_REFRESH_TOKEN)

        user = await self.user_service.get_by_id(UUID(user_id_str))
        if user is None or not user.is_active:
            logger.warning(REFRESH_FAILED_USER_MISSING_OR_INACTIVE, user_id_str)
            raise http_error(INVALID_REFRESH_TOKEN)

        new_access_token = create_access_token(str(user.id))
        response.set_cookie(
            key=ACCESS_TOKEN_COOKIE_NAME,
            value=new_access_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
        )

        role_name = await self.user_role_service.get_primary_role_name(user.id)
        logger.info(REFRESH_SUCCESS, user.id)

        return AuthResponse(
            user=AuthUserResponse(
                id=user.id,
                email=user.email,
                role=role_name,
            )
        )
