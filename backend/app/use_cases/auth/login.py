import logging

from app.schemas.auth.requests import LoginRequest
from app.schemas.auth.responses import AuthResponse, AuthUserResponse
from app.services.users.user_role_service import UserRoleService
from app.services.users.user_service import UserService
from app.utils.errors.http_errors import INVALID_CREDENTIALS, USER_INACTIVE, http_error
from app.utils.logging_setup.messages import (
    LOGIN_FAILED_INVALID_PASSWORD,
    LOGIN_FAILED_UNKNOWN_EMAIL,
    LOGIN_FAILED_USER_INACTIVE,
    LOGIN_SUCCESS,
)
from app.utils.password import verify_password

logger = logging.getLogger(__name__)


class LoginUseCase:
    def __init__(
        self,
        user_service: UserService,
        user_role_service: UserRoleService,
    ) -> None:
        self.user_service = user_service
        self.user_role_service = user_role_service

    async def execute(self, login_request: LoginRequest) -> AuthResponse:
        user = await self.user_service.get_by_email(login_request.email)
        if user is None:
            logger.warning(LOGIN_FAILED_UNKNOWN_EMAIL, login_request.email)
            raise http_error(INVALID_CREDENTIALS)

        if not verify_password(login_request.password, user.hashed_password):
            logger.warning(LOGIN_FAILED_INVALID_PASSWORD, user.id)
            raise http_error(INVALID_CREDENTIALS)

        if not user.is_active:
            logger.warning(LOGIN_FAILED_USER_INACTIVE, user.id)
            raise http_error(USER_INACTIVE)

        role_name = await self.user_role_service.get_primary_role_name(user.id)
        logger.info(LOGIN_SUCCESS, user.id)

        return AuthResponse(
            user=AuthUserResponse(
                id=user.id,
                email=user.email,
                role=role_name,
            )
        )
