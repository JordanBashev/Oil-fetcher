from fastapi import APIRouter, Cookie, Depends, Request, Response
from uuid import UUID

from app.config import (
    ACCESS_TOKEN_COOKIE_NAME,
    COOKIE_SAMESITE,
    REFRESH_TOKEN_COOKIE_NAME,
    settings,
)
from app.dependencies.auth import (
    get_login_use_case,
    get_refresh_use_case,
    get_register_use_case,
)
from app.schemas.auth.requests import LoginRequest, RegisterRequest
from app.schemas.auth.responses import AuthResponse
from app.utils.rate_limit.setup import limiter
from app.utils.tokens import create_access_token, create_refresh_token
from app.use_cases.auth.login import LoginUseCase
from app.use_cases.auth.logout import LogoutUseCase
from app.use_cases.auth.refresh import RefreshUseCase
from app.use_cases.auth.register import RegisterUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookies(response: Response, user_id: UUID) -> None:
    access_token = create_access_token(str(user_id))
    refresh_token = create_refresh_token(str(user_id))
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
    )
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
    )


@router.post("/register", response_model=AuthResponse, status_code=201)
@limiter.limit(lambda: settings.RATE_LIMIT_REGISTER)
async def register(
    request: Request,
    register_request: RegisterRequest,
    response: Response,
    use_case: RegisterUseCase = Depends(get_register_use_case),
) -> AuthResponse:
    result = await use_case.execute(register_request)
    _set_auth_cookies(response, result.user.id)
    return result


@router.post("/login", response_model=AuthResponse)
@limiter.limit(lambda: settings.RATE_LIMIT_LOGIN)
async def login(
    request: Request,
    login_request: LoginRequest,
    response: Response,
    use_case: LoginUseCase = Depends(get_login_use_case),
) -> AuthResponse:
    result = await use_case.execute(login_request)
    _set_auth_cookies(response, result.user.id)
    return result


@router.post("/logout")
async def logout(response: Response) -> dict:
    return LogoutUseCase().execute(response)


@router.post("/refresh", response_model=AuthResponse)
@limiter.limit(lambda: settings.RATE_LIMIT_REFRESH)
async def refresh(
    request: Request,
    response: Response,
    use_case: RefreshUseCase = Depends(get_refresh_use_case),
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_TOKEN_COOKIE_NAME),
) -> AuthResponse:
    return await use_case.execute(refresh_token, response)
