import pytest
from httpx import AsyncClient

NEW_FIRST_NAME = "Ada"
NEW_LAST_NAME = "Lovelace"
NEW_BIO = "Mathematician"


@pytest.mark.asyncio
async def test_get_profile_returns_current_user(registered_client: AsyncClient) -> None:
    response = await registered_client.get("/api/profile")

    assert response.status_code == 200
    body = response.json()
    assert body["email"] is not None


@pytest.mark.asyncio
async def test_update_profile_persists_changes(registered_client: AsyncClient) -> None:
    update_response = await registered_client.put(
        "/api/profile",
        json={"first_name": NEW_FIRST_NAME, "last_name": NEW_LAST_NAME, "bio": NEW_BIO},
    )
    assert update_response.status_code == 200

    fetched = await registered_client.get("/api/profile")
    assert fetched.status_code == 200
    body = fetched.json()
    assert body["first_name"] == NEW_FIRST_NAME
    assert body["last_name"] == NEW_LAST_NAME
    assert body["bio"] == NEW_BIO


@pytest.mark.asyncio
async def test_partial_update_only_changes_provided_fields(registered_client: AsyncClient) -> None:
    await registered_client.put(
        "/api/profile",
        json={"first_name": NEW_FIRST_NAME, "last_name": NEW_LAST_NAME, "bio": NEW_BIO},
    )

    await registered_client.put("/api/profile", json={"bio": "Updated bio only"})

    fetched = (await registered_client.get("/api/profile")).json()
    assert fetched["first_name"] == NEW_FIRST_NAME
    assert fetched["last_name"] == NEW_LAST_NAME
    assert fetched["bio"] == "Updated bio only"
