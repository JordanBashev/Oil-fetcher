from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession


class Transaction:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exception_type, exception, traceback) -> None:
        if exception_type is None:
            await self.session.commit()
        else:
            await self.session.rollback()
