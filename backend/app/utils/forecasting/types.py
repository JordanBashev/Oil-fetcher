from datetime import date
from enum import StrEnum
from typing import Callable

DAYS_PER_WEEK = 7
FIRST_FUTURE_STEP = 1


class ForecastModelType(StrEnum):
    LINEAR_REGRESSION_V1 = "linear_regression_v1"
    HOLT_WINTERS_V1 = "holt_winters_v1"


ForecastFunction = Callable[[list[tuple[date, float]], int], list[tuple[date, float]]]
