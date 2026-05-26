from uuid import UUID

from app.database.transaction import Transaction
from app.services.users.user_service import UserService
from app.utils.errors.http_errors import USER_NOT_FOUND, http_error
from app.utils.global_messages import USER_DELETED_MESSAGE


class DeleteUserUseCase:
    def __init__(self, transaction: Transaction, user_service: UserService) -> None:
        self.transaction = transaction
        self.user_service = user_service

    async def execute(self, user_id: UUID) -> dict:
        user = await self.user_service.get_by_id(user_id)
        if user is None:
            raise http_error(USER_NOT_FOUND)

        async with self.transaction:
            await self.user_service.delete(user_id)
        return {"detail": USER_DELETED_MESSAGE}
