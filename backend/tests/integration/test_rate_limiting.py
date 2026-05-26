"""Rate limiting — the second call hits 429."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.utils.rate_limit.setup import limiter
from tests.fixtures.auth import register
from tests.fixtures.data import seed_roles

ONE_PER_MINUTE = "1/minute"
FIRST_USER_EMAIL = "first@example.com"
SECOND_USER_EMAIL = "second@example.com"
TEST_PASSWORD = "strong-password-123"


@pytest.mark.asyncio
async def test_second_register_within_window_returns_429(
    test_session: AsyncSession,
    test_client: AsyncClient,
) -> None:
    """Verify the second call returns 429.

    The limiter is a process-wide singleton, so we clear its in-memory storage
    first to avoid bleed-through from other tests that already hit /register.
    """
    settings.RATE_LIMIT_REGISTER = ONE_PER_MINUTE
    limiter.reset()
    await seed_roles(test_session)

    first_response = await register(test_client, email=FIRST_USER_EMAIL, password=TEST_PASSWORD)
    assert first_response.status_code == 201

    second_response = await register(test_client, email=SECOND_USER_EMAIL, password=TEST_PASSWORD)

    assert second_response.status_code == 429
