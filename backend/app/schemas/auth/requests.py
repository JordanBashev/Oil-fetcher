from pydantic import BaseModel, EmailStr, field_validator

from app.config import MINIMUM_PASSWORD_LENGTH
from app.utils.global_messages import PASSWORD_TOO_SHORT_TEMPLATE


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_meets_minimum_length(cls, password: str) -> str:
        if len(password) < MINIMUM_PASSWORD_LENGTH:
            raise ValueError(PASSWORD_TOO_SHORT_TEMPLATE.format(minimum=MINIMUM_PASSWORD_LENGTH))
        return password


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
