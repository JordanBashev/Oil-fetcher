"""Forecast reproducibility — the headline assessment requirement.

A completed forecast pins to its DatasetVersion and is unchanged even after a
*new* DatasetVersion lands.

(Deterministic-prediction-from-identical-inputs is covered at the unit level in
test_forecasting.py — re-running an identical forecast through the HTTP API is
now blocked by the duplicate-prevention rule.)
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from tests.fixtures.data import (
    build_dataset_version,
    insert_price_history,
    seed_oil_dataset,
)
from tests.fixtures.polling import poll_until_terminal

SEEDED_WEEKS = 160
HOLT_WINTERS_MODEL = "holt_winters_v1"


async def _create_completed_forecast(client: AsyncClient, oil_series_id: UUID) -> dict:
    create_response = await client.post(
        "/api/forecasts",
        json={
            "forecast_model": HOLT_WINTERS_MODEL,
            "oil_series_id": str(oil_series_id),
        },
    )
    assert create_response.status_code == 202
    forecast_job_id = create_response.json()["id"]
    return await poll_until_terminal(client, forecast_job_id)


@pytest.mark.asyncio
async def test_forecast_stays_reproducible_after_new_dataset_version(
    test_session: AsyncSession,
    registered_client: AsyncClient,
) -> None:
    series, original_version = await seed_oil_dataset(test_session, weeks=SEEDED_WEEKS)

    forecast_body = await _create_completed_forecast(registered_client, series.id)
    original_points = [(point["period"], point["value"]) for point in forecast_body["points"]]
    assert forecast_body["dataset_version_id"] == str(original_version.id)

    new_version = build_dataset_version(hash="test-hash-revision-0002", record_count=SEEDED_WEEKS)
    test_session.add(new_version)
    await test_session.commit()
    await test_session.refresh(new_version)
    await insert_price_history(
        test_session,
        oil_series_id=series.id,
        dataset_version_id=new_version.id,
        weeks=SEEDED_WEEKS,
    )

    reread = await registered_client.get(f"/api/forecasts/{forecast_body['id']}")
    reread.raise_for_status()
    reread_body = reread.json()

    reread_points = [(point["period"], point["value"]) for point in reread_body["points"]]
    assert reread_points == original_points, "An existing forecast's points must never change"
    assert reread_body["dataset_version_id"] == str(original_version.id), "Pinning must not move"
    assert reread_body["is_based_on_latest_data"] is False, "After a new version, the flag must flip"
