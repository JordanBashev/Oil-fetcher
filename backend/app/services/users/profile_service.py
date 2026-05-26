from uuid import UUID

from app.database.models.users.profile import Profile
from app.repositories.users.profile_repository import ProfileRepository


class ProfileService:
    def __init__(self, profile_repository: ProfileRepository) -> None:
        self.profile_repository = profile_repository

    async def get_by_user_id(self, user_id: UUID) -> Profile | None:
        return await self.profile_repository.get_by_user_id(user_id)

    async def create(self, profile: Profile) -> Profile:
        return await self.profile_repository.create(profile)

    async def update(self, profile: Profile) -> Profile:
        return await self.profile_repository.update(profile)
