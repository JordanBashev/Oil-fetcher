import logging

from app.schemas.oil.requests import FetchMode
from app.services.oil.oil_fetch_runner import run_oil_fetch
from app.utils.logging_setup.messages import WEEKLY_OIL_REVISION_CREATED, WEEKLY_OIL_REVISION_SKIPPED

logger = logging.getLogger(__name__)


async def run_weekly_oil_revision() -> None:
    result = await run_oil_fetch(FetchMode.WEEKLY_REVISION)

    if result.created_version:
        logger.info(WEEKLY_OIL_REVISION_CREATED, result.dataset_version_id)
    else:
        logger.info(WEEKLY_OIL_REVISION_SKIPPED, result.skipped_reason)
