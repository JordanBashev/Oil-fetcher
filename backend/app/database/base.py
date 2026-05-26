from collections.abc import AsyncGenerator
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

SQLITE_URL_FILE_PREFIX = "sqlite"


def _ensure_sqlite_parent_directory_exists(database_url: str) -> None:
    if not database_url.startswith(SQLITE_URL_FILE_PREFIX):
        return
    file_path = Path(urlparse(database_url).path.lstrip("/"))
    file_path.parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_parent_directory_exists(settings.DATABASE_URL)
async_engine = create_async_engine(settings.DATABASE_URL)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
