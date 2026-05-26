import json
import logging
import re
from datetime import date, datetime
from pathlib import Path

from app.schemas.common.pagination import PaginationParams
from app.schemas.logs.requests import LogQueryFilters
from app.schemas.logs.responses import LogLineResponse
from app.utils.logging_setup.messages import LOG_READER_UNREADABLE_FILE

ACTIVE_LOG_BASENAME = "app.current.log"
ROTATED_LOG_FILENAME_REGEX = re.compile(r"^app\.(\d{4}-\d{2}-\d{2})_to_(\d{4}-\d{2}-\d{2})(?:\.\d+)?\.log$")
ISO_DATE_FORMAT = "%Y-%m-%d"

JSON_PARSE_ERROR_LEVEL = "ERROR"
JSON_PARSE_ERROR_LOGGER = "app.utils.logging_setup.log_reader"

logger = logging.getLogger(__name__)


def read_logs(
    log_dir: Path,
    filters: LogQueryFilters,
    pagination: PaginationParams,
    max_recent_scan_lines: int,
) -> tuple[list[LogLineResponse], int]:
    """Return a paginated slice of log entries matching the filters.

    Algorithm:
      1. List files in the log dir.
      2. If a date filter is set, keep only files whose filename-encoded range
         (or the active file, which always qualifies) overlaps the query.
      3. Otherwise, scan only the active file capped at max_recent_scan_lines.
      4. Parse each JSON line, apply the in-memory filters, sort newest-first.
      5. Return the requested page + the total count of matches.
    """
    candidate_files = _select_files(log_dir, filters)
    raw_lines = _read_candidate_lines(candidate_files, filters, max_recent_scan_lines)
    parsed_entries = _parse_and_filter(raw_lines, filters)

    parsed_entries.sort(key=lambda entry: entry.timestamp, reverse=True)
    total_count = len(parsed_entries)
    page_slice = parsed_entries[pagination.offset : pagination.offset + pagination.limit]
    return page_slice, total_count


def _select_files(log_dir: Path, filters: LogQueryFilters) -> list[Path]:
    if not log_dir.exists():
        return []

    active_path = log_dir / ACTIVE_LOG_BASENAME
    selected: list[Path] = []

    if filters.date_from is None and filters.date_to is None:
        if active_path.exists():
            selected.append(active_path)
        return selected

    for log_path in log_dir.iterdir():
        if not log_path.is_file():
            continue
        if log_path.name == ACTIVE_LOG_BASENAME:
            selected.append(log_path)
            continue
        file_range = _parse_rotated_range(log_path.name)
        if file_range is None:
            continue
        if _range_overlaps_filter(file_range, filters):
            selected.append(log_path)
    return selected


def _parse_rotated_range(filename: str) -> tuple[date, date] | None:
    match = ROTATED_LOG_FILENAME_REGEX.match(filename)
    if match is None:
        return None
    try:
        file_from = datetime.strptime(match.group(1), ISO_DATE_FORMAT).date()
        file_to = datetime.strptime(match.group(2), ISO_DATE_FORMAT).date()
    except ValueError:
        return None
    return file_from, file_to


def _range_overlaps_filter(file_range: tuple[date, date], filters: LogQueryFilters) -> bool:
    file_from, file_to = file_range
    if filters.date_to is not None and file_from > filters.date_to:
        return False
    if filters.date_from is not None and file_to < filters.date_from:
        return False
    return True


def _read_candidate_lines(
    candidate_files: list[Path],
    filters: LogQueryFilters,
    max_recent_scan_lines: int,
) -> list[str]:
    no_date_filter = filters.date_from is None and filters.date_to is None
    if no_date_filter and len(candidate_files) == 1:
        return _tail_lines(candidate_files[0], max_recent_scan_lines)

    collected: list[str] = []
    for log_path in candidate_files:
        try:
            with log_path.open("r", encoding="utf-8") as file_handle:
                collected.extend(file_handle.readlines())
        except OSError as read_error:
            logger.warning(LOG_READER_UNREADABLE_FILE, log_path, read_error)
    return collected


def _tail_lines(log_path: Path, max_lines: int) -> list[str]:
    try:
        with log_path.open("r", encoding="utf-8") as file_handle:
            all_lines = file_handle.readlines()
    except OSError as read_error:
        logger.warning(LOG_READER_UNREADABLE_FILE, log_path, read_error)
        return []
    return all_lines[-max_lines:]


def _parse_and_filter(raw_lines: list[str], filters: LogQueryFilters) -> list[LogLineResponse]:
    parsed: list[LogLineResponse] = []
    for raw_line in raw_lines:
        stripped = raw_line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            continue

        entry = LogLineResponse(
            timestamp=payload.get("timestamp"),
            level=payload.get("level", ""),
            logger=payload.get("logger", ""),
            message=payload.get("message", ""),
        )

        if not _entry_matches_filters(entry, filters):
            continue
        parsed.append(entry)
    return parsed


def _entry_matches_filters(entry: LogLineResponse, filters: LogQueryFilters) -> bool:
    if filters.level is not None and entry.level != filters.level.value:
        return False
    if filters.logger is not None and filters.logger.lower() not in entry.logger.lower():
        return False
    if filters.search is not None and filters.search.lower() not in entry.message.lower():
        return False
    if filters.date_from is not None and entry.timestamp.date() < filters.date_from:
        return False
    if filters.date_to is not None and entry.timestamp.date() > filters.date_to:
        return False
    return True
