import logging

from app.config import DEFAULT_ROLE
from app.database.models.users.profile import Profile
from app.database.models.users.user import User
from app.database.models.users.user_role import UserRole
from app.database.transaction import Transaction
from app.schemas.auth.requests import RegisterRequest
from app.schemas.auth.responses import AuthResponse, AuthUserResponse
from app.services.users.profile_service import ProfileService
from app.services.users.role_service import RoleService
from app.services.users.user_role_service import UserRoleService
from app.services.users.user_service import UserService
from app.utils.errors.http_errors import DEFAULT_ROLE_MISSING, EMAIL_TAKEN, http_error
from app.utils.logging_setup.messages import (
    REGISTER_FAILED_DEFAULT_ROLE_MISSING,
    REGISTER_REJECTED_EMAIL_TAKEN,
    REGISTER_SUCCESS,
)
from app.utils.password import hash_password

logger = logging.getLogger(__name__)


class RegisterUseCase:
    def __init__(
        self,
        transaction: Transaction,
        user_service: UserService,
        profile_service: ProfileService,
        role_service: RoleService,
        user_role_service: UserRoleService,
    ) -> None:
        self.transaction = transaction
        self.user_service = user_service
        self.profile_service = profile_service
        self.role_service = role_service
        self.user_role_service = user_role_service

    async def execute(self, register_request: RegisterRequest) -> AuthResponse:
        if await self.user_service.email_is_taken(register_request.email):
            logger.warning(REGISTER_REJECTED_EMAIL_TAKEN, register_request.email)
            raise http_error(EMAIL_TAKEN)

        default_role = await self.role_service.get_by_name(DEFAULT_ROLE)
        if default_role is None:
            logger.error(REGISTER_FAILED_DEFAULT_ROLE_MISSING, DEFAULT_ROLE)
            raise http_error(DEFAULT_ROLE_MISSING)

        async with self.transaction:
            user = await self.user_service.create(
                User(
                    email=register_request.email,
                    hashed_password=hash_password(register_request.password),
                )
            )
            await self.profile_service.create(Profile(user_id=user.id))
            await self.user_role_service.assign_role(
                UserRole(user_id=user.id, role_id=default_role.id)
            )

        logger.info(REGISTER_SUCCESS, user.id)

        return AuthResponse(
            user=AuthUserResponse(
                id=user.id,
                email=user.email,
                roles=[default_role.name],
            )
        )
