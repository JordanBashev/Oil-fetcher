import logging
import queue
import sys
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path

from app.config import settings
from app.utils.logging_setup.dated_rotating_handler import DatedRotatingFileHandler
from app.utils.logging_setup.json_formatter import JsonLineFormatter

CONSOLE_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
CONSOLE_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_queue_listener: QueueListener | None = None


def setup_logging() -> None:
    """Wire up async-safe logging for the whole application.

    A QueueHandler is installed on the root logger so log calls in request
    handlers are non-blocking (just enqueue + return). A background
    QueueListener thread drains the queue and dispatches each record to
    the real handlers (console + rotating JSON file).
    """
    global _queue_listener

    log_queue: queue.Queue = queue.Queue(maxsize=settings.LOG_QUEUE_MAX_SIZE)

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(logging.Formatter(CONSOLE_FORMAT, datefmt=CONSOLE_DATE_FORMAT))

    file_handler = DatedRotatingFileHandler(
        log_dir=Path(settings.LOG_DIR),
        max_bytes=settings.LOG_FILE_MAX_BYTES,
        backup_count=settings.LOG_FILE_BACKUP_COUNT,
    )
    file_handler.setFormatter(JsonLineFormatter())

    queue_handler = QueueHandler(log_queue)

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL.upper())
    root_logger.handlers.clear()
    root_logger.addHandler(queue_handler)

    _queue_listener = QueueListener(log_queue, console_handler, file_handler, respect_handler_level=True)
    _queue_listener.start()


def shutdown_logging() -> None:
    """Flush and stop the background log listener so no records are lost on exit."""
    global _queue_listener
    if _queue_listener is not None:
        _queue_listener.stop()
        _queue_listener = None
