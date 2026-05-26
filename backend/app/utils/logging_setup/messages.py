"""Named log message templates.

Format strings only — pass arguments to `logger.<level>(TEMPLATE, *args)` so
the formatter handles substitution lazily. Names follow `<AREA>_<EVENT>`.
"""

# --- auth ---
AUTH_ACCESS_DENIED_INVALID_TOKEN = "Access denied: invalid access token"
AUTH_ACCESS_DENIED_USER_MISSING_OR_INACTIVE = "Access denied: user id=%s missing or inactive"
AUTH_ADMIN_ACCESS_DENIED = "Admin access denied for user id=%s"

# --- login ---
LOGIN_FAILED_UNKNOWN_EMAIL = "Login failed: unknown email=%s"
LOGIN_FAILED_INVALID_PASSWORD = "Login failed: invalid password for user id=%s"
LOGIN_FAILED_USER_INACTIVE = "Login failed: user id=%s is inactive"
LOGIN_SUCCESS = "Login success: user id=%s"

# --- register ---
REGISTER_REJECTED_EMAIL_TAKEN = "Registration rejected: email already taken (email=%s)"
REGISTER_FAILED_DEFAULT_ROLE_MISSING = "Registration failed: default role %s is missing"
REGISTER_SUCCESS = "Registered user id=%s"

# --- refresh ---
REFRESH_FAILED_MISSING_TOKEN = "Refresh failed: missing refresh token"
REFRESH_FAILED_INVALID_TOKEN = "Refresh failed: invalid or expired refresh token"
REFRESH_FAILED_USER_MISSING_OR_INACTIVE = "Refresh failed: user id=%s missing or inactive"
REFRESH_SUCCESS = "Refresh success: user id=%s"

# --- forecast job ---
FORECAST_JOB_STARTED = "Forecast job %s started (model=%s, history=%s, horizon=%s)"
FORECAST_JOB_COMPLETED = "Forecast job %s completed with %s points"
FORECAST_JOB_FAILED = "Forecast job %s failed: %s"
FORECAST_JOB_CRASHED = "Forecast job %s crashed"

# --- user seeder ---
USER_SEEDER_CREATED = "User seeder created user %s"
USER_SEEDER_SKIPPED = "User seeder skipped: %s"

# --- oil fetch (shared by seeder + scheduler jobs) ---
OIL_SEEDER_CREATED = "Oil seeder created dataset version %s with %s records"
OIL_SEEDER_SKIPPED = "Oil seeder skipped: %s"
DAILY_OIL_FETCH_CREATED = "Daily oil fetch created dataset version %s"
DAILY_OIL_FETCH_SKIPPED = "Daily oil fetch skipped: %s"
WEEKLY_OIL_REVISION_CREATED = "Weekly oil revision created dataset version %s"
WEEKLY_OIL_REVISION_SKIPPED = "Weekly oil revision skipped: %s"

# --- log reader ---
LOG_READER_UNREADABLE_FILE = "Skipping unreadable log file %s: %s"
