from datetime import datetime, timezone
from logging import LogRecord
from logging.handlers import RotatingFileHandler
from pathlib import Path

ACTIVE_LOG_BASENAME = "app.current.log"
ROTATED_LOG_FILENAME_TEMPLATE = "app.{date_from}_to_{date_to}.log"
TIMESTAMP_DATE_FORMAT = "%Y-%m-%d"


class DatedRotatingFileHandler(RotatingFileHandler):
    """RotatingFileHandler that renames rotated files to encode their date range.

    Active file: app.current.log
    Rotated:     app.<first-iso-date>_to_<last-iso-date>.log

    The first and last dates come from the log records themselves, tracked
    in memory. This lets the admin log reader filter files by their filename
    without opening each one to peek at the bookends.
    """

    def __init__(
        self,
        log_dir: Path,
        max_bytes: int,
        backup_count: int,
    ) -> None:
        log_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir = log_dir
        active_path = log_dir / ACTIVE_LOG_BASENAME
        super().__init__(
            filename=str(active_path),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        self._first_record_date: str | None = None
        self._last_record_date: str | None = None

    def emit(self, record: LogRecord) -> None:
        record_date = datetime.fromtimestamp(record.created, tz=timezone.utc).strftime(TIMESTAMP_DATE_FORMAT)
        if self._first_record_date is None:
            self._first_record_date = record_date
        self._last_record_date = record_date
        super().emit(record)

    def doRollover(self) -> None:
        # Close the active stream so the rename is safe.
        if self.stream is not None:
            self.stream.close()
            self.stream = None

        active_path = Path(self.baseFilename)
        if active_path.exists() and self._first_record_date is not None and self._last_record_date is not None:
            rotated_name = ROTATED_LOG_FILENAME_TEMPLATE.format(
                date_from=self._first_record_date,
                date_to=self._last_record_date,
            )
            rotated_path = self.log_dir / self._resolve_collision(rotated_name)
            active_path.rename(rotated_path)

        # Reset the date trackers for the new active file.
        self._first_record_date = None
        self._last_record_date = None
        self._prune_oldest_backups()

        if not self.delay:
            self.stream = self._open()

    def _resolve_collision(self, candidate_name: str) -> str:
        # If two rotations happen on the same day with the same date range,
        # append a numeric suffix so we never overwrite an existing file.
        candidate_path = self.log_dir / candidate_name
        if not candidate_path.exists():
            return candidate_name

        base = candidate_path.stem
        suffix = candidate_path.suffix
        collision_index = 1
        while True:
            alternative = f"{base}.{collision_index}{suffix}"
            if not (self.log_dir / alternative).exists():
                return alternative
            collision_index += 1

    def _prune_oldest_backups(self) -> None:
        if self.backupCount <= 0:
            return
        rotated_files = sorted(
            self.log_dir.glob("app.*_to_*.log"),
            key=lambda path: path.stat().st_mtime,
        )
        overflow = len(rotated_files) - self.backupCount
        for stale_file in rotated_files[:overflow]:
            stale_file.unlink(missing_ok=True)
