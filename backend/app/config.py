from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_ROLE = "user"
ADMIN_ROLE = "admin"
SEEDED_ROLES = (DEFAULT_ROLE, ADMIN_ROLE)

ACCESS_TOKEN_COOKIE_NAME = "access_token"
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"

TOKEN_TYPE_CLAIM = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

SUBJECT_CLAIM = "sub"

COOKIE_SAMESITE = "lax"

MINIMUM_PASSWORD_LENGTH = 8


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/app.db"
    SECRET_KEY: str = "change-me-to-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRY_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRY_DAYS: int = 7
    FRONTEND_ORIGIN: str = "http://localhost:3000"
    COOKIE_SECURE: bool = False
    EIA_API_KEY: str = "change-me-to-your-eia-api-key"

    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "./data/logs"
    LOG_FILE_MAX_BYTES: int = 100_000_000
    LOG_FILE_BACKUP_COUNT: int = 100
    LOG_QUEUE_MAX_SIZE: int = 10_000
    LOG_MAX_RECENT_SCAN_LINES: int = 5_000

    RATE_LIMIT_REGISTER: str = "1/minute"
    RATE_LIMIT_LOGIN: str = "1/minute"
    RATE_LIMIT_REFRESH: str = "1/minute"
    RATE_LIMIT_FORECAST_CREATE: str = "1/minute"
    RATE_LIMIT_OIL_FETCH: str = "1/minute"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
