from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.users.profile_repository import ProfileRepository
from app.repositories.users.role_repository import RoleRepository
from app.repositories.users.user_repository import UserRepository
from app.repositories.users.user_role_repository import UserRoleRepository
from app.services.users.profile_service import ProfileService
from app.services.users.role_service import RoleService
from app.services.users.user_role_service import UserRoleService
from app.services.users.user_service import UserService


@dataclass
class UserServices:
    users: UserService
    roles: RoleService
    user_roles: UserRoleService
    profiles: ProfileService


def build_user_services(session: AsyncSession) -> UserServices:
    role_repository = RoleRepository(session)
    return UserServices(
        users=UserService(UserRepository(session)),
        roles=RoleService(role_repository),
        user_roles=UserRoleService(UserRoleRepository(session), role_repository),
        profiles=ProfileService(ProfileRepository(session)),
    )
