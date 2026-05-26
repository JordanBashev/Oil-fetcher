from pathlib import Path

from app.config import settings
from app.schemas.common.pagination import PaginationMeta, PaginationParams
from app.schemas.logs.requests import LogQueryFilters
from app.schemas.logs.responses import PaginatedLogsResponse
from app.utils.logging_setup.log_reader import read_logs


class ListLogsUseCase:
    async def execute(
        self,
        filters: LogQueryFilters,
        pagination: PaginationParams,
    ) -> PaginatedLogsResponse:
        items, total_count = read_logs(
            log_dir=Path(settings.LOG_DIR),
            filters=filters,
            pagination=pagination,
            max_recent_scan_lines=settings.LOG_MAX_RECENT_SCAN_LINES,
        )
        return PaginatedLogsResponse(
            items=items,
            pagination=PaginationMeta.build(total_count, pagination),
        )
