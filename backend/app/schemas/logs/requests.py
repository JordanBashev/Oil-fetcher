from datetime import date
from enum import StrEnum

from pydantic import BaseModel


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogQueryFilters(BaseModel):
    level: LogLevel | None = None
    logger: str | None = None
    search: str | None = None
    date_from: date | None = None
    date_to: date | None = None
