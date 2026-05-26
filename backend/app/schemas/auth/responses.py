from uuid import UUID

from pydantic import BaseModel


class AuthUserResponse(BaseModel):
    id: UUID
    email: str
    role: str


class AuthResponse(BaseModel):
    user: AuthUserResponse
