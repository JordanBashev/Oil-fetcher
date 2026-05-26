from logging.config import fileConfig
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import engine_from_config, pool

from alembic import context

from app.config import settings
from app.database import Base
import app.database.models  # noqa: F401  -- ensures all models register with Base.metadata


SQLITE_ASYNC_DRIVER_PREFIX = "sqlite+aiosqlite://"
SQLITE_SYNC_DRIVER_PREFIX = "sqlite://"
SQLITE_URL_FILE_PREFIX = "sqlite"


def _sync_url_for_alembic(database_url: str) -> str:
    if database_url.startswith(SQLITE_ASYNC_DRIVER_PREFIX):
        return SQLITE_SYNC_DRIVER_PREFIX + database_url[len(SQLITE_ASYNC_DRIVER_PREFIX):]
    return database_url


def _ensure_sqlite_parent_directory_exists(database_url: str) -> None:
    if not database_url.startswith(SQLITE_URL_FILE_PREFIX):
        return
    file_path = Path(urlparse(database_url).path.lstrip("/"))
    file_path.parent.mkdir(parents=True, exist_ok=True)


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

if not config.get_main_option("sqlalchemy.url"):
    sync_url = _sync_url_for_alembic(settings.DATABASE_URL)
    _ensure_sqlite_parent_directory_exists(sync_url)
    config.set_main_option("sqlalchemy.url", sync_url)

target_metadata = Base.metadata


def generate_migrations_and_run() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def generate_migrations_and_run_against_database() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    generate_migrations_and_run()
else:
    generate_migrations_and_run_against_database()
