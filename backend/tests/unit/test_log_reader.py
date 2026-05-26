"""Unit tests for the log reader.

Focus on the file-selection layer (which files get opened given filters) and
the JSON parsing. The filename-range overlap logic is the load-bearing piece
for the date_from / date_to query parameters on /admin/logs.
"""
import json
from datetime import date, datetime, timezone
from pathlib import Path

from app.schemas.common.pagination import PaginationParams
from app.schemas.logs.requests import LogLevel, LogQueryFilters
from app.utils.logging_setup.log_reader import (
    ACTIVE_LOG_BASENAME,
    read_logs,
)

MAX_SCAN_LINES = 5_000


def _write_json_lines(path: Path, lines: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(line) for line in lines) + "\n",
        encoding="utf-8",
    )


def _entry(
    timestamp: datetime,
    level: str = "INFO",
    logger_name: str = "app.x",
    message: str = "hello",
) -> dict:
    return {
        "timestamp": timestamp.isoformat(),
        "level": level,
        "logger": logger_name,
        "message": message,
    }


def test_reads_active_file_when_no_date_filter(tmp_path: Path) -> None:
    active_path = tmp_path / ACTIVE_LOG_BASENAME
    _write_json_lines(
        active_path,
        [
            _entry(datetime(2026, 5, 22, 14, 0, 0, tzinfo=timezone.utc), message="first"),
            _entry(datetime(2026, 5, 22, 14, 1, 0, tzinfo=timezone.utc), message="second"),
        ],
    )

    items, total = read_logs(
        log_dir=tmp_path,
        filters=LogQueryFilters(),
        pagination=PaginationParams(page=1, items_per_page=10),
        max_recent_scan_lines=MAX_SCAN_LINES,
    )

    assert total == 2
    assert {item.message for item in items} == {"first", "second"}


def test_level_filter_drops_non_matches(tmp_path: Path) -> None:
    active_path = tmp_path / ACTIVE_LOG_BASENAME
    _write_json_lines(
        active_path,
        [
            _entry(datetime(2026, 5, 22, 14, 0, tzinfo=timezone.utc), level="INFO"),
            _entry(datetime(2026, 5, 22, 14, 1, tzinfo=timezone.utc), level="ERROR"),
            _entry(datetime(2026, 5, 22, 14, 2, tzinfo=timezone.utc), level="WARNING"),
        ],
    )

    items, total = read_logs(
        log_dir=tmp_path,
        filters=LogQueryFilters(level=LogLevel.ERROR),
        pagination=PaginationParams(page=1, items_per_page=10),
        max_recent_scan_lines=MAX_SCAN_LINES,
    )

    assert total == 1
    assert items[0].level == "ERROR"


def test_date_filter_picks_rotated_files_by_filename_range(tmp_path: Path) -> None:
    # Two rotated files with distinct ranges; only one overlaps the query.
    in_range_path = tmp_path / "app.2026-01-01_to_2026-01-31.log"
    out_of_range_path = tmp_path / "app.2025-01-01_to_2025-01-31.log"
    _write_json_lines(
        in_range_path,
        [_entry(datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc), message="in")],
    )
    _write_json_lines(
        out_of_range_path,
        [_entry(datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc), message="out")],
    )

    items, total = read_logs(
        log_dir=tmp_path,
        filters=LogQueryFilters(date_from=date(2026, 1, 1), date_to=date(2026, 1, 31)),
        pagination=PaginationParams(page=1, items_per_page=10),
        max_recent_scan_lines=MAX_SCAN_LINES,
    )

    assert total == 1
    assert items[0].message == "in"


def test_results_are_newest_first(tmp_path: Path) -> None:
    active_path = tmp_path / ACTIVE_LOG_BASENAME
    _write_json_lines(
        active_path,
        [
            _entry(datetime(2026, 5, 22, 14, 0, tzinfo=timezone.utc), message="older"),
            _entry(datetime(2026, 5, 22, 14, 5, tzinfo=timezone.utc), message="newer"),
        ],
    )

    items, _total = read_logs(
        log_dir=tmp_path,
        filters=LogQueryFilters(),
        pagination=PaginationParams(page=1, items_per_page=10),
        max_recent_scan_lines=MAX_SCAN_LINES,
    )

    assert [item.message for item in items] == ["newer", "older"]
