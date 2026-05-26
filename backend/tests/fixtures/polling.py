"""Polling helpers for endpoints that run work in BackgroundTasks."""
import asyncio
from uuid import UUID

from httpx import AsyncClient

from app.database.models.forecasts.forecast_job import ForecastStatus

DEFAULT_POLL_INTERVAL_SECONDS = 0.05
DEFAULT_POLL_TIMEOUT_SECONDS = 10.0
TERMINAL_STATUSES = {ForecastStatus.COMPLETED, ForecastStatus.FAILED, ForecastStatus.CANCELED}


async def poll_until_terminal(
    client: AsyncClient,
    forecast_job_id: UUID,
    timeout_seconds: float = DEFAULT_POLL_TIMEOUT_SECONDS,
    interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS,
) -> dict:
    """GET the forecast until its status is terminal; return the final response body."""
    deadline = asyncio.get_event_loop().time() + timeout_seconds
    while asyncio.get_event_loop().time() < deadline:
        response = await client.get(f"/api/forecasts/{forecast_job_id}")
        response.raise_for_status()
        body = response.json()
        if body["status"] in TERMINAL_STATUSES:
            return body
        await asyncio.sleep(interval_seconds)
    raise TimeoutError(f"Forecast {forecast_job_id} did not reach a terminal status in {timeout_seconds}s")
