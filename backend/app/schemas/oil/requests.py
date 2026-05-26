from enum import Enum

from pydantic import BaseModel


class FetchMode(str, Enum):
    HISTORICAL = "historical"
    DAILY = "daily"
    WEEKLY_REVISION = "weekly_revision"


class OilFetchRequest(BaseModel):
    mode: FetchMode = FetchMode.DAILY
