from datetime import date, timedelta

import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from app.utils.forecasting.types import DAYS_PER_WEEK, FIRST_FUTURE_STEP

SEASONAL_PERIOD_WEEKS = 52

TREND_TYPE_ADDITIVE = "add"
SEASONAL_TYPE_ADDITIVE = "add"
INITIALIZATION_METHOD = "estimated"


def holt_winters_forecast(
    history: list[tuple[date, float]],
    horizon_weeks: int,
) -> list[tuple[date, float]]:
    """Holt-Winters triple exponential smoothing (level + trend + 52-week seasonality).

    Requires at least 2 full seasonal cycles of history. Deterministic.
    """
    history_values = np.array([value for _, value in history], dtype=float)

    fitted_model = ExponentialSmoothing(
        history_values,
        trend=TREND_TYPE_ADDITIVE,
        seasonal=SEASONAL_TYPE_ADDITIVE,
        seasonal_periods=SEASONAL_PERIOD_WEEKS,
        initialization_method=INITIALIZATION_METHOD,
    ).fit()

    predictions = fitted_model.forecast(steps=horizon_weeks)

    last_history_period = history[-1][0]
    future_points: list[tuple[date, float]] = []
    for step in range(FIRST_FUTURE_STEP, horizon_weeks + FIRST_FUTURE_STEP):
        future_period = last_history_period + timedelta(days=DAYS_PER_WEEK * step)
        predicted_value = float(predictions[step - FIRST_FUTURE_STEP])
        future_points.append((future_period, predicted_value))

    return future_points
