import logging

from app.schemas.oil.requests import FetchMode
from app.services.oil.oil_fetch_runner import run_oil_fetch
from app.utils.logging_setup.messages import OIL_SEEDER_CREATED, OIL_SEEDER_SKIPPED

logger = logging.getLogger(__name__)


async def seed_oil() -> None:
    """Populate the database with 5 years of historical oil prices.

    Runs the oil fetch in HISTORICAL mode. The use case skips itself if a
    dataset version already exists, so running the seeder twice is safe.
    """
    print("Seeding oil data...")
    result = await run_oil_fetch(FetchMode.HISTORICAL)

    if result.created_version:
        print("Seeding oil data completed.")
        logger.info(OIL_SEEDER_CREATED, result.dataset_version_id, result.record_count)
    else:
        print("Seeding oil data skipped.")
        logger.info(OIL_SEEDER_SKIPPED, result.skipped_reason)
