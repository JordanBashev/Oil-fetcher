import logging

from app.schemas.oil.requests import FetchMode
from app.services.oil.oil_fetch_runner import run_oil_fetch
from app.utils.logging_setup.messages import DAILY_OIL_FETCH_CREATED, DAILY_OIL_FETCH_SKIPPED

logger = logging.getLogger(__name__)


async def run_daily_oil_fetch() -> None:
    result = await run_oil_fetch(FetchMode.DAILY)

    if result.created_version:
        logger.info(DAILY_OIL_FETCH_CREATED, result.dataset_version_id)
    else:
        logger.info(DAILY_OIL_FETCH_SKIPPED, result.skipped_reason)
