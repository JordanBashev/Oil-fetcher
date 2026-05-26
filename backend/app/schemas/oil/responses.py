from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OilFetchResultResponse(BaseModel):
    created_version: bool
    dataset_version_id: UUID | None = None
    record_count: int = 0
    skipped_reason: str | None = None


class OilSeriesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    series: str
    series_description: str
    duoarea: str
    area_name: str
    product: str
    product_name: str
    process: str
    process_name: str
    units: str


class OilPricePoint(BaseModel):
    period: date
    value: float


class OilPriceSeries(BaseModel):
    series_code: str
    series_description: str
    points: list[OilPricePoint]


class OilPricesResponse(BaseModel):
    is_aggregated: bool
    matched_series_count: int
    date_from: date | None = None
    date_to: date | None = None
    unit_label: str | None = None
    series: list[OilPriceSeries]
