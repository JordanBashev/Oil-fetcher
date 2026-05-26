from uuid import UUID

from app.database.models.users.user import User
from app.repositories.users.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.user_repository.get_by_id(user_id)

    async def get_by_email(self, email: str) -> User | None:
        return await self.user_repository.get_by_email(email)

    async def email_is_taken(self, email: str) -> bool:
        return await self.user_repository.get_by_email(email) is not None

    async def get_all(self) -> list[User]:
        return await self.user_repository.get_all()

    async def get_all_with_roles(self) -> list[User]:
        return await self.user_repository.get_all_with_roles()

    async def create(self, user: User) -> User:
        return await self.user_repository.create(user)

    async def update(self, user: User) -> User:
        return await self.user_repository.update(user)

    async def delete(self, user_id: UUID) -> None:
        await self.user_repository.delete(user_id)
