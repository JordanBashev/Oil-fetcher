from dataclasses import dataclass

from fastapi import HTTPException, status


@dataclass(frozen=True)
class ErrorDefinition:
    status_code: int
    detail: str


# Auth errors
INVALID_CREDENTIALS = ErrorDefinition(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
NOT_AUTHENTICATED = ErrorDefinition(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
INVALID_TOKEN = ErrorDefinition(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
INVALID_REFRESH_TOKEN = ErrorDefinition(status.HTTP_401_UNAUTHORIZED, "Invalid or expired refresh token")
USER_INACTIVE = ErrorDefinition(status.HTTP_403_FORBIDDEN, "Account is deactivated")
ADMIN_REQUIRED = ErrorDefinition(status.HTTP_403_FORBIDDEN, "Admin access required")

# Resource errors
USER_NOT_FOUND = ErrorDefinition(status.HTTP_404_NOT_FOUND, "User not found")
PROFILE_NOT_FOUND = ErrorDefinition(status.HTTP_404_NOT_FOUND, "Profile not found")
ROLE_NOT_FOUND = ErrorDefinition(status.HTTP_404_NOT_FOUND, "Role not found")
ROLE_NOT_ASSIGNED = ErrorDefinition(status.HTTP_404_NOT_FOUND, "Role not assigned to user")
FORECAST_NOT_FOUND = ErrorDefinition(status.HTTP_404_NOT_FOUND, "Forecast not found")
NO_DATASET_AVAILABLE = ErrorDefinition(status.HTTP_404_NOT_FOUND, "No dataset version available to forecast against")

# Validation errors
HISTORICAL_FETCH_NOT_ALLOWED = ErrorDefinition(
    status.HTTP_400_BAD_REQUEST,
    "Historical fetch is only run by the seeder, not the fetch endpoint",
)
# Conflict errors
EMAIL_TAKEN = ErrorDefinition(status.HTTP_409_CONFLICT, "Email already registered")
ROLE_ALREADY_ASSIGNED = ErrorDefinition(status.HTTP_409_CONFLICT, "Role already assigned to user")
FORECAST_NOT_CANCELABLE = ErrorDefinition(
    status.HTTP_409_CONFLICT,
    "Only pending forecasts can be canceled",
)
FORECAST_ALREADY_EXISTS = ErrorDefinition(
    status.HTTP_409_CONFLICT,
    "An identical forecast (same model, target, and dataset) is already pending, processing, or completed",
)

# Server errors
DEFAULT_ROLE_MISSING = ErrorDefinition(status.HTTP_500_INTERNAL_SERVER_ERROR, "Default role not found")


def http_error(error: ErrorDefinition) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.detail)
