"""Plain auth helpers used across integration tests."""
from httpx import AsyncClient, Response

DEFAULT_TEST_EMAIL = "user@example.com"
DEFAULT_TEST_PASSWORD = "strong-password-123"


async def register(
    client: AsyncClient,
    email: str = DEFAULT_TEST_EMAIL,
    password: str = DEFAULT_TEST_PASSWORD,
) -> Response:
    return await client.post("/api/auth/register", json={"email": email, "password": password})


async def login(
    client: AsyncClient,
    email: str = DEFAULT_TEST_EMAIL,
    password: str = DEFAULT_TEST_PASSWORD,
) -> Response:
    return await client.post("/api/auth/login", json={"email": email, "password": password})
