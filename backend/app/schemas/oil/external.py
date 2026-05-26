from datetime import date

from pydantic import BaseModel


class EiaPriceRow(BaseModel):
    """Data returned by the EIA petroleum prices endpoint."""

    period: date
    duoarea: str
    area_name: str
    product: str
    product_name: str
    process: str
    process_name: str
    series: str
    series_description: str
    value: float
    units: str
