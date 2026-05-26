from app.database.models.users.user import User
from app.database.transaction import Transaction
from app.schemas.users.requests import ProfileUpdateRequest
from app.schemas.users.responses import ProfileResponse
from app.services.users.profile_service import ProfileService
from app.utils.errors.http_errors import PROFILE_NOT_FOUND, http_error


class UpdateProfileUseCase:
    def __init__(self, transaction: Transaction, profile_service: ProfileService) -> None:
        self.transaction = transaction
        self.profile_service = profile_service

    async def execute(self, current_user: User, profile_update_request: ProfileUpdateRequest) -> ProfileResponse:
        profile = await self.profile_service.get_by_user_id(current_user.id)
        if profile is None:
            raise http_error(PROFILE_NOT_FOUND)

        async with self.transaction:
            for field_name, value in profile_update_request.model_dump(exclude_none=True).items():
                setattr(profile, field_name, value)
            updated_profile = await self.profile_service.update(profile)

        return ProfileResponse(
            first_name=updated_profile.first_name,
            last_name=updated_profile.last_name,
            bio=updated_profile.bio,
            email=current_user.email,
        )