from app.utils.forecasting.holt_winters import holt_winters_forecast
from app.utils.forecasting.linear_regression import linear_regression_forecast
from app.utils.forecasting.types import ForecastFunction, ForecastModelType

LINEAR_REGRESSION_HISTORY_WEEKS = 104
HOLT_WINTERS_HISTORY_WEEKS = 156
SYSTEM_FORECAST_HORIZON_WEEKS = 8

FORECAST_FUNCTIONS: dict[ForecastModelType, ForecastFunction] = {
    ForecastModelType.LINEAR_REGRESSION_V1: linear_regression_forecast,
    ForecastModelType.HOLT_WINTERS_V1: holt_winters_forecast,
}

MODEL_HISTORY_WEEKS: dict[ForecastModelType, int] = {
    ForecastModelType.LINEAR_REGRESSION_V1: LINEAR_REGRESSION_HISTORY_WEEKS,
    ForecastModelType.HOLT_WINTERS_V1: HOLT_WINTERS_HISTORY_WEEKS,
}
