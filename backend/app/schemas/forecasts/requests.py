from typing import Self
from uuid import UUID

from pydantic import BaseModel, model_validator

from app.utils.forecasting.types import ForecastModelType


class ForecastTarget(BaseModel):
    oil_series_id: UUID | None = None
    units: str | None = None

    @model_validator(mode="after")
    def validate_exactly_one(self) -> Self:
        if self.oil_series_id is not None and self.units is not None:
            raise ValueError("Specify either oil_series_id (single series) or units (aggregate), not both")
        if self.oil_series_id is None and self.units is None:
            raise ValueError("Specify either oil_series_id (single series) or units (aggregate)")
        return self


class CreateForecastRequest(ForecastTarget):
    forecast_model: ForecastModelType
