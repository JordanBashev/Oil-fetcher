from math import ceil
from typing import Self

from pydantic import BaseModel, Field

DEFAULT_ITEMS_PER_PAGE = 10
MIN_ITEMS_PER_PAGE = 1
MAX_ITEMS_PER_PAGE = 100
FIRST_PAGE = 1


class PaginationParams(BaseModel):
    page: int = Field(default=FIRST_PAGE, ge=FIRST_PAGE)
    items_per_page: int = Field(default=DEFAULT_ITEMS_PER_PAGE, ge=MIN_ITEMS_PER_PAGE, le=MAX_ITEMS_PER_PAGE)

    @property
    def offset(self) -> int:
        return (self.page - FIRST_PAGE) * self.items_per_page

    @property
    def limit(self) -> int:
        return self.items_per_page


class PaginationMeta(BaseModel):
    total_count: int
    items_per_page: int
    current_page: int
    total_pages: int

    @classmethod
    def build(cls, total_count: int, params: PaginationParams) -> Self:
        total_pages = ceil(total_count / params.items_per_page) if total_count > 0 else 0
        return cls(
            total_count=total_count,
            items_per_page=params.items_per_page,
            current_page=params.page,
            total_pages=total_pages,
        )
