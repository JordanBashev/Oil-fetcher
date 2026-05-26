from datetime import date
from uuid import UUID

from pydantic import BaseModel

DEFAULT_OIL_UNIT = "$/BBL"


class OilPriceRecordFilters(BaseModel):
    oil_series_id: UUID | None = None
    dataset_version_id: UUID | None = None
    date_from: date | None = None
    date_to: date | None = None
    duoarea: str | None = None
    product: str | None = None
    process: str | None = None
    units: str | None = None
