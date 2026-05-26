"""Auth flow integration tests — proves the security story end-to-end."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ACCESS_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_NAME
from tests.fixtures.auth import DEFAULT_TEST_EMAIL, login, register
from tests.fixtures.data import seed_roles

WRONG_PASSWORD = "definitely-wrong"


@pytest.mark.asyncio
async def test_register_creates_user_and_sets_cookies(test_session: AsyncSession, test_client: AsyncClient) -> None:
    await seed_roles(test_session)

    response = await register(test_client)

    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == DEFAULT_TEST_EMAIL
    assert body["user"]["role"] == "user"
    assert ACCESS_TOKEN_COOKIE_NAME in response.cookies
    assert REFRESH_TOKEN_COOKIE_NAME in response.cookies


@pytest.mark.asyncio
async def test_duplicate_register_returns_409(test_session: AsyncSession, test_client: AsyncClient) -> None:
    await seed_roles(test_session)
    await register(test_client)

    response = await register(test_client)

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_with_correct_credentials_succeeds(test_session: AsyncSession, test_client: AsyncClient) -> None:
    await seed_roles(test_session)
    await register(test_client)
    test_client.cookies.clear()

    response = await login(test_client)

    assert response.status_code == 200
    assert ACCESS_TOKEN_COOKIE_NAME in response.cookies


@pytest.mark.asyncio
async def test_login_with_wrong_password_returns_401(test_session: AsyncSession, test_client: AsyncClient) -> None:
    await seed_roles(test_session)
    await register(test_client)

    response = await login(test_client, password=WRONG_PASSWORD)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_with_unknown_email_returns_401(test_session: AsyncSession, test_client: AsyncClient) -> None:
    await seed_roles(test_session)

    response = await login(test_client, email="nobody@example.com")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_without_cookies_returns_401(test_client: AsyncClient) -> None:
    response = await test_client.get("/api/profile")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_valid_cookies_succeeds(registered_client: AsyncClient) -> None:
    response = await registered_client.get("/api/profile")

    assert response.status_code == 200
    assert response.json()["email"] == DEFAULT_TEST_EMAIL


@pytest.mark.asyncio
async def test_refresh_issues_new_access_token(registered_client: AsyncClient) -> None:
    response = await registered_client.post("/api/auth/refresh")

    assert response.status_code == 200
    assert ACCESS_TOKEN_COOKIE_NAME in response.cookies


@pytest.mark.asyncio
async def test_refresh_without_token_returns_401(test_client: AsyncClient) -> None:
    response = await test_client.post("/api/auth/refresh")

    assert response.status_code == 401
