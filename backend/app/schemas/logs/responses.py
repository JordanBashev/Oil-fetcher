from datetime import datetime

from pydantic import BaseModel

from app.schemas.common.pagination import PaginationMeta


class LogLineResponse(BaseModel):
    timestamp: datetime
    level: str
    logger: str
    message: str


class PaginatedLogsResponse(BaseModel):
    items: list[LogLineResponse]
    pagination: PaginationMeta
