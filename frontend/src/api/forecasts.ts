import { apiClient } from "./client";

export const FORECAST_STATUS = {
  PENDING: "pending",
  PROCESSING: "processing",
  COMPLETED: "completed",
  FAILED: "failed",
  CANCELED: "canceled",
} as const;

export type ForecastStatus = (typeof FORECAST_STATUS)[keyof typeof FORECAST_STATUS];

export const FORECAST_MODEL = {
  LINEAR_REGRESSION_V1: "linear_regression_v1",
  HOLT_WINTERS_V1: "holt_winters_v1",
} as const;

export type ForecastModel = (typeof FORECAST_MODEL)[keyof typeof FORECAST_MODEL];

export const TERMINAL_FORECAST_STATUSES: ForecastStatus[] = [
  FORECAST_STATUS.COMPLETED,
  FORECAST_STATUS.FAILED,
  FORECAST_STATUS.CANCELED,
];

export type ForecastPoint = {
  period: string;
  value: number;
};

export type ForecastJob = {
  id: string;
  user_id: string;
  status: ForecastStatus;

  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;

  dataset_version_id: string;
  forecast_model: ForecastModel;
  history_weeks: number;
  horizon_weeks: number;

  oil_series_id: string | null;
  units: string | null;

  is_based_on_latest_data: boolean;
  points: ForecastPoint[];
};

export type PaginationMeta = {
  page: number;
  items_per_page: number;
  total_count: number;
  total_pages: number;
};

export type PaginatedForecasts = {
  items: ForecastJob[];
  pagination: PaginationMeta;
};

export type ForecastTarget = {
  oil_series_id?: string;
  units?: string;
};

export type CreateForecastBody = ForecastTarget & {
  forecast_model: ForecastModel;
};

export type ListForecastsParams = {
  page: number;
  items_per_page: number;
};

export async function createForecastRequest(body: CreateForecastBody): Promise<ForecastJob> {
  const { data } = await apiClient.post<ForecastJob>("/forecasts", body);
  return data;
}

export async function listForecastsRequest(params: ListForecastsParams): Promise<PaginatedForecasts> {
  const { data } = await apiClient.get<PaginatedForecasts>("/forecasts", { params });
  return data;
}

export async function getForecastRequest(forecastId: string): Promise<ForecastJob> {
  const { data } = await apiClient.get<ForecastJob>(`/forecasts/${forecastId}`);
  return data;
}

export async function getLatestMatchingForecastRequest(
  target: ForecastTarget,
  forecastModel?: ForecastModel,
): Promise<ForecastJob | null> {
  const { data } = await apiClient.get<ForecastJob | null>("/forecasts/latest-matching", {
    params: { ...target, forecast_model: forecastModel },
  });
  return data;
}

export async function cancelForecastRequest(forecastId: string): Promise<ForecastJob> {
  const { data } = await apiClient.post<ForecastJob>(`/forecasts/${forecastId}/cancel`);
  return data;
}

export async function deleteForecastRequest(forecastId: string): Promise<void> {
  await apiClient.delete(`/forecasts/${forecastId}`);
}
