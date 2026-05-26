"""Oil read endpoints — series listing, filtered prices, aggregate vs per-series mode."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fixtures.data import build_oil_series, insert_price_history, seed_oil_dataset

OIL_SERIES_COUNT_FOR_AGGREGATE = 8  # > MAX_INDIVIDUAL_SERIES (6) so the response aggregates
PER_SERIES_SAFE_COUNT = 3
WEEKS_PER_SERIES = 12


@pytest.mark.asyncio
async def test_list_series_returns_seeded_series(
    test_session: AsyncSession,
    registered_client: AsyncClient,
) -> None:
    series, _version = await seed_oil_dataset(test_session, weeks=20)

    response = await registered_client.get("/api/oil/series")

    assert response.status_code == 200
    body = response.json()
    series_codes = {entry["series"] for entry in body}
    assert series.series in series_codes


@pytest.mark.asyncio
async def test_prices_per_series_when_few_match(
    test_session: AsyncSession,
    registered_client: AsyncClient,
) -> None:
    series, version = await seed_oil_dataset(test_session, weeks=WEEKS_PER_SERIES)

    response = await registered_client.get(f"/api/oil/prices?oil_series_id={series.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["is_aggregated"] is False
    assert body["matched_series_count"] == 1
    assert len(body["series"]) == 1
    assert body["series"][0]["series_code"] == series.series
    assert len(body["series"][0]["points"]) == WEEKS_PER_SERIES


@pytest.mark.asyncio
async def test_prices_aggregate_when_many_series_match(
    test_session: AsyncSession,
    registered_client: AsyncClient,
) -> None:
    _series_one, version = await seed_oil_dataset(test_session, weeks=WEEKS_PER_SERIES)

    # Add enough additional series so the total exceeds the per-series threshold.
    for index in range(OIL_SERIES_COUNT_FOR_AGGREGATE - 1):
        extra_series = build_oil_series(series=f"TEST_EXTRA_{index}")
        test_session.add(extra_series)
        await test_session.commit()
        await test_session.refresh(extra_series)
        await insert_price_history(
            test_session,
            oil_series_id=extra_series.id,
            dataset_version_id=version.id,
            weeks=WEEKS_PER_SERIES,
        )

    response = await registered_client.get("/api/oil/prices?units=$/BBL")

    assert response.status_code == 200
    body = response.json()
    assert body["is_aggregated"] is True
    assert body["matched_series_count"] == OIL_SERIES_COUNT_FOR_AGGREGATE
    assert body["unit_label"] == "$/BBL"
    assert len(body["series"]) == 1  # one synthetic aggregate line
    assert body["series"][0]["series_code"] == "AGGREGATE"


@pytest.mark.asyncio
async def test_prices_unit_filter_excludes_other_units(
    test_session: AsyncSession,
    registered_client: AsyncClient,
) -> None:
    await seed_oil_dataset(test_session, weeks=WEEKS_PER_SERIES)  # $/BBL series
    # Add a $/GAL series; filter on $/BBL should not include it.
    gas_series = build_oil_series(series="TEST_GAS", units="$/GAL", product="EPMRR")
    test_session.add(gas_series)
    await test_session.commit()

    response = await registered_client.get("/api/oil/prices?units=$/BBL")

    assert response.status_code == 200
    assert response.json()["matched_series_count"] == 1
