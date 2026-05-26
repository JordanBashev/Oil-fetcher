from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    SUBJECT_CLAIM,
    TOKEN_TYPE_CLAIM,
    settings,
)

EXPIRATION_CLAIM = "exp"


class TokenError(Exception):
    pass


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    payload = {
        SUBJECT_CLAIM: subject,
        TOKEN_TYPE_CLAIM: token_type,
        EXPIRATION_CLAIM: datetime.now(timezone.utc) + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str) -> str:
    return _create_token(
        subject=subject,
        token_type=ACCESS_TOKEN_TYPE,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY_MINUTES),
    )


def create_refresh_token(subject: str) -> str:
    return _create_token(
        subject=subject,
        token_type=REFRESH_TOKEN_TYPE,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRY_DAYS),
    )


def decode_token(token: str, expected_type: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as decode_error:
        raise TokenError("invalid token") from decode_error

    actual_type = payload.get(TOKEN_TYPE_CLAIM)
    if actual_type != expected_type:
        raise TokenError(f"expected {expected_type} token, got {actual_type}")

    subject = payload.get(SUBJECT_CLAIM)
    if not subject:
        raise TokenError("missing subject claim")
    return subject
