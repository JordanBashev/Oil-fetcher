"""Test data builders.

Each helper inserts the minimum required rows for whatever a test asserts on.
We bypass the EIA client entirely — these tests never make network calls.
Defaults are tuned to satisfy the strictest forecast model's minimum (104 weeks).
"""
from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ADMIN_ROLE, DEFAULT_ROLE
from app.database.models.oil.dataset_version import DatasetVersion
from app.database.models.oil.oil_price_record import OilPriceRecord
from app.database.models.oil.oil_series import OilSeries
from app.database.models.users.role import Role

DAYS_PER_WEEK = 7
FIRST_PERIOD = date(2024, 1, 1)
BASE_VALUE = 100.0
VALUE_STEP = 0.5


async def seed_roles(session: AsyncSession) -> None:
    """Insert the user/admin roles the auth flow expects. Idempotent."""
    from sqlalchemy import select

    existing = await session.execute(select(Role.name))
    existing_names = {row[0] for row in existing.all()}
    for role_name in (DEFAULT_ROLE, ADMIN_ROLE):
        if role_name not in existing_names:
            session.add(Role(name=role_name))
    await session.commit()


def build_oil_series(**overrides) -> OilSeries:
    defaults = dict(
        series="TEST_RWTC",
        series_description="Test crude oil weekly spot",
        duoarea="NUS",
        area_name="U.S.",
        product="EPCWTI",
        product_name="Crude Oil",
        process="PE1",
        process_name="Spot Price",
        units="$/BBL",
    )
    return OilSeries(**(defaults | overrides))


def build_dataset_version(**overrides) -> DatasetVersion:
    defaults = dict(
        fetched_at=datetime.now(timezone.utc),
        hash="test-hash-0001",
        record_count=104,
        date_from=FIRST_PERIOD,
        date_to=date.fromordinal(FIRST_PERIOD.toordinal() + DAYS_PER_WEEK * 103),
        source="TEST",
    )
    return DatasetVersion(**(defaults | overrides))


async def insert_price_history(
    session: AsyncSession,
    oil_series_id: UUID,
    dataset_version_id: UUID,
    weeks: int,
) -> None:
    """Insert `weeks` consecutive weekly points with a deterministic ramp: 100, 100.5, 101..."""
    for week_index in range(weeks):
        period = date.fromordinal(FIRST_PERIOD.toordinal() + DAYS_PER_WEEK * week_index)
        session.add(
            OilPriceRecord(
                oil_series_id=oil_series_id,
                dataset_version_id=dataset_version_id,
                period=period,
                value=BASE_VALUE + VALUE_STEP * week_index,
            )
        )
    await session.commit()


async def seed_oil_dataset(session: AsyncSession, weeks: int = 110) -> tuple[OilSeries, DatasetVersion]:
    """Build one series + one version + N weekly price points. Returns the pair."""
    series = build_oil_series()
    session.add(series)
    await session.commit()
    await session.refresh(series)

    version = build_dataset_version(record_count=weeks)
    session.add(version)
    await session.commit()
    await session.refresh(version)

    await insert_price_history(session, series.id, version.id, weeks)
    return series, version
