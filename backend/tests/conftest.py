"""Shared test setup.

Every test gets a fresh in-memory SQLite database and a FastAPI app with:
  - the request-scoped session dependency overridden to point at it,
  - the module-level `async_session_maker` (used by background tasks like
    the forecast worker) patched to point at the same in-memory DB,
  - rate limits relaxed so test suites can hammer endpoints without 429.
"""
import tempfile
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.config import settings

# Redirect logs to a throwaway temp dir before app.main imports and calls
# setup_logging(), otherwise tests would litter the project root with logs.
settings.LOG_DIR = tempfile.mkdtemp(prefix="oil-forecaster-tests-")

from app.database import base as database_base  # noqa: E402
from app.database.base import Base, get_db  # noqa: E402

import app.database.models  # noqa: F401, E402 — populates Base.metadata

RELAXED_RATE_LIMIT = "100000/minute"
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_BASE_URL = "http://test"


@pytest_asyncio.fixture
async def test_engine_and_factory():
    """One in-memory engine + sessionmaker per test, schema created up front."""
    # StaticPool keeps one connection alive for the whole engine lifetime so
    # the in-memory DB persists across the async session checkouts.
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield engine, factory
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine_and_factory) -> AsyncGenerator[AsyncSession, None]:
    """A clean in-memory SQLite session for direct DB seeding inside tests."""
    _engine, factory = test_engine_and_factory
    async with factory() as session:
        yield session


@pytest_asyncio.fixture
async def test_client(
    test_engine_and_factory,
    test_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """FastAPI app wired against the test session, with rate limits relaxed.

    Two overrides:
      1. Dependency override on get_db -> request handlers use the test session.
      2. Monkey-patch app.database.base.async_session_maker -> background tasks
         (forecast worker, oil fetcher) open sessions from the in-memory DB too.
    """
    _relax_rate_limits()

    from app.main import app

    _engine, factory = test_engine_and_factory

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    original_session_maker = database_base.async_session_maker
    database_base.async_session_maker = factory

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=TEST_BASE_URL) as client:
        yield client

    app.dependency_overrides.clear()
    database_base.async_session_maker = original_session_maker


def _relax_rate_limits() -> None:
    settings.RATE_LIMIT_REGISTER = RELAXED_RATE_LIMIT
    settings.RATE_LIMIT_LOGIN = RELAXED_RATE_LIMIT
    settings.RATE_LIMIT_REFRESH = RELAXED_RATE_LIMIT
    settings.RATE_LIMIT_FORECAST_CREATE = RELAXED_RATE_LIMIT
    settings.RATE_LIMIT_OIL_FETCH = RELAXED_RATE_LIMIT


@pytest_asyncio.fixture
async def registered_client(
    test_session: AsyncSession,
    test_client: AsyncClient,
) -> AsyncClient:
    """A test client that has already registered (and thus logged in) the default user.

    Seeds the user/admin roles, registers the default test user, and returns
    the same client with auth cookies set. Tests that need an authenticated
    request flow can take this fixture instead of test_client to skip the
    register/login boilerplate.
    """
    from tests.fixtures.auth import register
    from tests.fixtures.data import seed_roles

    await seed_roles(test_session)
    await register(test_client)
    return test_client
