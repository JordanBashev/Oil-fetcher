"""Unit tests for the forecasting functions.

Both functions must be deterministic — same input, same output — because every
stored forecast depends on this property to remain reproducible.
"""
from datetime import date, timedelta

import pytest

from app.utils.forecasting.dispatcher import (
    HOLT_WINTERS_HISTORY_WEEKS,
    LINEAR_REGRESSION_HISTORY_WEEKS,
)
from app.utils.forecasting.holt_winters import SEASONAL_PERIOD_WEEKS, holt_winters_forecast
from app.utils.forecasting.linear_regression import linear_regression_forecast
from app.utils.forecasting.types import DAYS_PER_WEEK

LINEAR_TEST_HORIZON_WEEKS = 4
HOLT_WINTERS_TEST_HORIZON_WEEKS = 12


def _ramp_history(start_period: date, weeks: int, base: float, step: float) -> list[tuple[date, float]]:
    return [
        (start_period + timedelta(days=DAYS_PER_WEEK * week_index), base + step * week_index)
        for week_index in range(weeks)
    ]


def test_linear_regression_extends_the_ramp() -> None:
    """A perfectly linear input must yield the perfect line extrapolation."""
    history = _ramp_history(date(2024, 1, 1), weeks=10, base=100.0, step=2.0)

    predictions = linear_regression_forecast(history, horizon_weeks=LINEAR_TEST_HORIZON_WEEKS)

    assert len(predictions) == LINEAR_TEST_HORIZON_WEEKS
    expected_first_value = 100.0 + 2.0 * 10  # next week after history
    assert predictions[0][1] == pytest.approx(expected_first_value)
    assert predictions[-1][1] == pytest.approx(100.0 + 2.0 * (10 + LINEAR_TEST_HORIZON_WEEKS - 1))


def test_linear_regression_periods_step_weekly() -> None:
    history = _ramp_history(date(2024, 1, 1), weeks=5, base=50.0, step=1.0)

    predictions = linear_regression_forecast(history, horizon_weeks=3)

    expected_first_period = date(2024, 1, 1) + timedelta(days=DAYS_PER_WEEK * 5)
    assert predictions[0][0] == expected_first_period
    assert predictions[1][0] == expected_first_period + timedelta(days=DAYS_PER_WEEK)
    assert predictions[2][0] == expected_first_period + timedelta(days=DAYS_PER_WEEK * 2)


def test_linear_regression_is_deterministic() -> None:
    """Re-running with identical inputs must produce identical outputs."""
    history = _ramp_history(date(2024, 1, 1), weeks=20, base=75.0, step=1.5)

    first_run = linear_regression_forecast(history, horizon_weeks=8)
    second_run = linear_regression_forecast(history, horizon_weeks=8)

    assert first_run == second_run


def test_linear_regression_system_history_is_sane() -> None:
    assert LINEAR_REGRESSION_HISTORY_WEEKS >= 2


def test_holt_winters_returns_horizon_points() -> None:
    history = _ramp_history(
        date(2024, 1, 1),
        weeks=HOLT_WINTERS_HISTORY_WEEKS,
        base=100.0,
        step=0.25,
    )

    predictions = holt_winters_forecast(history, horizon_weeks=HOLT_WINTERS_TEST_HORIZON_WEEKS)

    assert len(predictions) == HOLT_WINTERS_TEST_HORIZON_WEEKS


def test_holt_winters_is_deterministic() -> None:
    history = _ramp_history(
        date(2024, 1, 1),
        weeks=HOLT_WINTERS_HISTORY_WEEKS,
        base=100.0,
        step=0.25,
    )

    first_run = holt_winters_forecast(history, horizon_weeks=HOLT_WINTERS_TEST_HORIZON_WEEKS)
    second_run = holt_winters_forecast(history, horizon_weeks=HOLT_WINTERS_TEST_HORIZON_WEEKS)

    assert first_run == second_run


def test_holt_winters_system_history_covers_two_seasonal_cycles() -> None:
    assert HOLT_WINTERS_HISTORY_WEEKS >= 2 * SEASONAL_PERIOD_WEEKS
