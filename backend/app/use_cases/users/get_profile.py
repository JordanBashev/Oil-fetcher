from app.database.models.users.user import User
from app.schemas.users.responses import ProfileResponse
from app.services.users.profile_service import ProfileService
from app.utils.errors.http_errors import PROFILE_NOT_FOUND, http_error


class GetProfileUseCase:
    def __init__(self, profile_service: ProfileService) -> None:
        self.profile_service = profile_service

    async def execute(self, current_user: User) -> ProfileResponse:
        profile = await self.profile_service.get_by_user_id(current_user.id)
        if profile is None:
            raise http_error(PROFILE_NOT_FOUND)

        return ProfileResponse(
            first_name=profile.first_name,
            last_name=profile.last_name,
            bio=profile.bio,
            email=current_user.email,
        )