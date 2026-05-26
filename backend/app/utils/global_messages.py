"""Plain string constants used outside HTTP error responses.

Messages that get stored in DB columns (e.g. ForecastJob.error_message),
written to logs, or returned in successful response fields like
OilFetchResultResponse.skipped_reason. HTTP errors live in
errors/http_errors.py with ErrorDefinition.
"""

EMPTY_HISTORY_MESSAGE = "No historical data found for the forecast's pinned dataset version and filters"

FETCH_SKIPPED_NO_DATA = "EIA returned no data for the requested range"
FETCH_SKIPPED_DUPLICATE = "Fetched data is identical to an existing dataset version"
FETCH_SKIPPED_HISTORICAL_EXISTS = "Historical data already exists; historical fetch skipped"

AGGREGATE_SERIES_CODE = "AGGREGATE"
AGGREGATE_DESCRIPTION_TEMPLATE = "Average of {count} series"

LOGOUT_SUCCESS_MESSAGE = "Logged out"
USER_DELETED_MESSAGE = "User deleted"
FORECAST_DELETED_MESSAGE = "Forecast deleted"

PASSWORD_TOO_SHORT_TEMPLATE = "Password must be at least {minimum} characters"
