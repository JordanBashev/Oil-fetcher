from fastapi import APIRouter, Depends

from app.database.models.users.user import User
from app.dependencies.users import get_profile_use_case, get_update_profile_use_case
from app.schemas.users.requests import ProfileUpdateRequest
from app.schemas.users.responses import ProfileResponse
from app.use_cases.users.get_profile import GetProfileUseCase
from app.use_cases.users.update_profile import UpdateProfileUseCase
from app.utils.auth import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    use_case: GetProfileUseCase = Depends(get_profile_use_case),
) -> ProfileResponse:
    return await use_case.execute(current_user)


@router.put("", response_model=ProfileResponse)
async def update_profile(
    profile_update_request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    use_case: UpdateProfileUseCase = Depends(get_update_profile_use_case),
) -> ProfileResponse:
    return await use_case.execute(current_user, profile_update_request)
