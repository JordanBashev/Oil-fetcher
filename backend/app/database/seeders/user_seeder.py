import logging

from app.config import ADMIN_ROLE, DEFAULT_ROLE
from app.database.base import async_session_maker
from app.database.models.users.profile import Profile
from app.database.models.users.user import User
from app.database.models.users.user_role import UserRole
from app.repositories.users.profile_repository import ProfileRepository
from app.repositories.users.role_repository import RoleRepository
from app.repositories.users.user_repository import UserRepository
from app.repositories.users.user_role_repository import UserRoleRepository
from app.utils.logging_setup.messages import (
    USER_SEEDER_CREATED,
    USER_SEEDER_SKIPPED,
)
from app.utils.password import hash_password

logger = logging.getLogger(__name__)

SEED_ADMIN_EMAIL = "admin@example.com"
SEED_ADMIN_PASSWORD = "admin12345"
SEED_USER_EMAIL = "user@example.com"
SEED_USER_PASSWORD = "user12345"


async def seed_users() -> None:
    """Idempotent: skips users that already exist by email."""
    async with async_session_maker() as session:
        print("Seeding users...")

        user_repository = UserRepository(session)
        profile_repository = ProfileRepository(session)
        role_repository = RoleRepository(session)
        user_role_repository = UserRoleRepository(session)

        default_role = await role_repository.get_by_name(DEFAULT_ROLE)
        admin_role = await role_repository.get_by_name(ADMIN_ROLE)
        if default_role is None or admin_role is None:
            logger.warning(USER_SEEDER_SKIPPED, "seeded roles missing — run migrations first")
            return

        await _create_user_if_missing(
            email=SEED_ADMIN_EMAIL,
            password=SEED_ADMIN_PASSWORD,
            role_ids=[default_role.id, admin_role.id],
            user_repository=user_repository,
            profile_repository=profile_repository,
            user_role_repository=user_role_repository,
        )
        await _create_user_if_missing(
            email=SEED_USER_EMAIL,
            password=SEED_USER_PASSWORD,
            role_ids=[default_role.id],
            user_repository=user_repository,
            profile_repository=profile_repository,
            user_role_repository=user_role_repository,
        )

        await session.commit()


async def _create_user_if_missing(
    email: str,
    password: str,
    role_ids: list,
    user_repository: UserRepository,
    profile_repository: ProfileRepository,
    user_role_repository: UserRoleRepository,
) -> None:
    existing_user = await user_repository.get_by_email(email)
    if existing_user is not None:
        logger.info(USER_SEEDER_SKIPPED, email)
        return

    created_user = await user_repository.create(
        User(email=email, hashed_password=hash_password(password))
    )
    await profile_repository.create(Profile(user_id=created_user.id))
    for role_id in role_ids:
        await user_role_repository.assign_role(
            UserRole(user_id=created_user.id, role_id=role_id)
        )
    logger.info(USER_SEEDER_CREATED, email)
