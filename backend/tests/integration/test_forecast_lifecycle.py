"""Forecast async lifecycle: PENDING -> PROCESSING -> COMPLETED / FAILED / CANCELED."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database.models.forecasts.forecast_job import ForecastStatus
from app.utils.forecasting.dispatcher import SYSTEM_FORECAST_HORIZON_WEEKS
from tests.fixtures.auth import register
from tests.fixtures.data import seed_oil_dataset, seed_roles
from tests.fixtures.polling import poll_until_terminal

HOLT_WINTERS_MODEL = "holt_winters_v1"
LINEAR_REGRESSION_MODEL = "linear_regression_v1"
SEEDED_WEEKS = 160

SECOND_USER_EMAIL = "second@example.com"
SECOND_USER_PASSWORD = "strong-password-123"


def _create_payload(oil_series_id: UUID, forecast_model: str = HOLT_WINTERS_MODEL) -> dict:
    return {
        "forecast_model": forecast_model,
        "oil_series_id": str(oil_series_id),
    }


@pytest.mark.asyncio
async def test_create_forecast_returns_pending_and_completes(
    test_session: AsyncSession,
    registered_client: AsyncClient,
) -> None:
    series, _version = await seed_oil_dataset(test_session, weeks=SEEDED_WEEKS)

    create_response = await registered_client.post("/api/forecasts", json=_create_payload(series.id))
    assert create_response.status_code == 202
    pending_body = create_response.json()
    assert pending_body["status"] == ForecastStatus.PENDING

    final_body = await poll_until_terminal(registered_client, pending_body["id"])
    assert final_body["status"] == ForecastStatus.COMPLETED
    assert len(final_body["points"]) == SYSTEM_FORECAST_HORIZON_WEEKS


@pytest.mark.asyncio
async def test_delete_forecast_removes_it(
    test_session: AsyncSession,
    registered_client: AsyncClient,
) -> None:
    series, _version = await seed_oil_dataset(test_session, weeks=SEEDED_WEEKS)
    create_response = await registered_client.post("/api/forecasts", json=_create_payload(series.id))
    forecast_job_id = create_response.json()["id"]
    await poll_until_terminal(registered_client, forecast_job_id)

    delete_response = await registered_client.delete(f"/api/forecasts/{forecast_job_id}")
    assert delete_response.status_code == 200

    reread = await registered_client.get(f"/api/forecasts/{forecast_job_id}")
    assert reread.status_code == 404


@pytest.mark.asyncio
async def test_user_cannot_see_other_users_forecast(
    test_session: AsyncSession,
    test_client: AsyncClient,
    registered_client: AsyncClient,
) -> None:
    """The default user creates a forecast. A second user must not be able to read it."""
    series, _version = await seed_oil_dataset(test_session, weeks=SEEDED_WEEKS)
    create_response = await registered_client.post("/api/forecasts", json=_create_payload(series.id))
    forecast_job_id = create_response.json()["id"]
    await poll_until_terminal(registered_client, forecast_job_id)

    second_client = test_client
    second_client.cookies.clear()
    await seed_roles(test_session)
    await register(second_client, email=SECOND_USER_EMAIL, password=SECOND_USER_PASSWORD)

    response = await second_client.get(f"/api/forecasts/{forecast_job_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_forecasts_only_returns_current_users(
    test_session: AsyncSession,
    registered_client: AsyncClient,
) -> None:
    series, _version = await seed_oil_dataset(test_session, weeks=SEEDED_WEEKS)
    create_response = await registered_client.post("/api/forecasts", json=_create_payload(series.id))
    forecast_job_id = create_response.json()["id"]
    await poll_until_terminal(registered_client, forecast_job_id)

    response = await registered_client.get("/api/forecasts")

    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total_count"] == 1
    assert body["items"][0]["id"] == forecast_job_id
