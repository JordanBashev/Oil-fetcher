from datetime import date

import httpx

from app.config import settings
from app.schemas.oil.external import EiaPriceRow
from app.services.oil.external.eia_constants import (
    EIA_BASE_URL,
    EIA_DATA_FREQUENCY,
    EIA_PETROLEUM_PRICES_ROUTE,
    EIA_REQUEST_TIMEOUT_SECONDS,
    EIA_SORT_COLUMN,
    EIA_SORT_DIRECTION,
    EIA_VALUE_COLUMN,
)

# EIA returns some field names with hyphens, which are not valid Python
# attribute names. This maps the raw JSON keys to our schema field names.
EIA_RESPONSE_FIELD_MAP = {
    "period": "period",
    "duoarea": "duoarea",
    "area-name": "area_name",
    "product": "product",
    "product-name": "product_name",
    "process": "process",
    "process-name": "process_name",
    "series": "series",
    "series-description": "series_description",
    "value": "value",
    "units": "units",
}

RESPONSE_KEY = "response"
DATA_KEY = "data"
TOTAL_KEY = "total"
MAX_ROWS_PER_REQUEST = 5000
FIRST_PAGE_OFFSET = 0


class EiaClient:
    """Fetches oil price data from the external EIA petroleum prices API."""

    async def fetch_prices(self, date_from: date, date_to: date) -> list[EiaPriceRow]:
        request_url = f"{EIA_BASE_URL}{EIA_PETROLEUM_PRICES_ROUTE}"
        collected_rows: list[EiaPriceRow] = []
        current_offset = FIRST_PAGE_OFFSET

        async with httpx.AsyncClient(timeout=EIA_REQUEST_TIMEOUT_SECONDS) as http_client:
            while True:
                response_section = await self._fetch_page(
                    http_client, request_url, date_from, date_to, current_offset
                )
                raw_rows = response_section.get(DATA_KEY, [])
                collected_rows.extend(self._parse_row(raw_row) for raw_row in raw_rows)

                total_available = int(response_section.get(TOTAL_KEY, len(collected_rows)))
                current_offset += len(raw_rows)

                no_more_rows = len(raw_rows) == 0
                all_rows_collected = current_offset >= total_available
                if no_more_rows or all_rows_collected:
                    break

        return collected_rows

    async def _fetch_page(
        self,
        http_client: httpx.AsyncClient,
        request_url: str,
        date_from: date,
        date_to: date,
        offset: int,
    ) -> dict:
        request_params = {
            "api_key": settings.EIA_API_KEY,
            "frequency": EIA_DATA_FREQUENCY,
            "data[0]": EIA_VALUE_COLUMN,
            "start": date_from.isoformat(),
            "end": date_to.isoformat(),
            "sort[0][column]": EIA_SORT_COLUMN,
            "sort[0][direction]": EIA_SORT_DIRECTION,
            "length": MAX_ROWS_PER_REQUEST,
            "offset": offset,
        }
        api_response = await http_client.get(request_url, params=request_params)
        api_response.raise_for_status()
        response_body = api_response.json()
        return response_body.get(RESPONSE_KEY, {})

    def _parse_row(self, raw_row: dict) -> EiaPriceRow:
        mapped_row = {}
        for raw_key, schema_field in EIA_RESPONSE_FIELD_MAP.items():
            mapped_row[schema_field] = raw_row.get(raw_key)
        return EiaPriceRow(**mapped_row)
