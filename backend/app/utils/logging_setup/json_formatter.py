import json
import logging
from datetime import datetime, timezone


class JsonLineFormatter(logging.Formatter):
    """Render each log record as one JSON object per line.

    Used by the file handler so the admin log endpoint can parse entries
    deterministically. The console keeps a human-readable format.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info is not None:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)
