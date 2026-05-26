from datetime import date, timedelta

import numpy as np

from app.utils.forecasting.types import DAYS_PER_WEEK, FIRST_FUTURE_STEP

LINEAR_REGRESSION_DEGREE = 1

def linear_regression_forecast(
    history: list[tuple[date, float]],
    horizon_weeks: int,
) -> list[tuple[date, float]]:
    """Project future weekly values using ordinary least-squares linear regression.

    Fits y = slope * x + intercept where x is the week index (0..len(history)-1)
    and y is the historical value. Future weeks step weekly from the last
    history period. Deterministic.
    """
    history_indices = np.arange(len(history), dtype=float)
    history_values = np.array([value for _, value in history], dtype=float)

    slope, intercept = np.polyfit(history_indices, history_values, LINEAR_REGRESSION_DEGREE)

    last_history_period = history[-1][0]
    future_points: list[tuple[date, float]] = []
    for step in range(FIRST_FUTURE_STEP, horizon_weeks + FIRST_FUTURE_STEP):
        future_index = len(history) - 1 + step
        predicted_value = float(slope * future_index + intercept)
        future_period = last_history_period + timedelta(days=DAYS_PER_WEEK * step)
        future_points.append((future_period, predicted_value))

    return future_points
