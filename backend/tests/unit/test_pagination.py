import pytest
from pydantic import ValidationError

from app.schemas.common.pagination import (
    DEFAULT_ITEMS_PER_PAGE,
    MAX_ITEMS_PER_PAGE,
    PaginationMeta,
    PaginationParams,
)


def test_offset_for_first_page_is_zero() -> None:
    params = PaginationParams(page=1, items_per_page=10)
    assert params.offset == 0
    assert params.limit == 10


def test_offset_advances_by_items_per_page() -> None:
    params = PaginationParams(page=3, items_per_page=25)
    assert params.offset == 50  # (3 - 1) * 25
    assert params.limit == 25


def test_defaults_match_documented_constants() -> None:
    params = PaginationParams()
    assert params.page == 1
    assert params.items_per_page == DEFAULT_ITEMS_PER_PAGE


def test_invalid_page_is_rejected() -> None:
    with pytest.raises(ValidationError):
        PaginationParams(page=0)


def test_items_per_page_upper_bound_is_enforced() -> None:
    with pytest.raises(ValidationError):
        PaginationParams(items_per_page=MAX_ITEMS_PER_PAGE + 1)


def test_meta_computes_total_pages_correctly() -> None:
    params = PaginationParams(page=1, items_per_page=10)

    meta = PaginationMeta.build(total_count=47, params=params)

    assert meta.total_count == 47
    assert meta.total_pages == 5  # 47 / 10 -> 5 pages
    assert meta.current_page == 1
    assert meta.items_per_page == 10


def test_meta_total_pages_is_zero_when_no_results() -> None:
    params = PaginationParams()

    meta = PaginationMeta.build(total_count=0, params=params)

    assert meta.total_pages == 0
