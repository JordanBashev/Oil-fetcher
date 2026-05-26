from uuid import UUID

from pydantic import BaseModel


class ProfileUpdateRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    bio: str | None = None


class UserStatusRequest(BaseModel):
    is_active: bool


class AssignRoleRequest(BaseModel):
    role_id: UUID
