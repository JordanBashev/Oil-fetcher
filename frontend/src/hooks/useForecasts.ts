import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  cancelForecastRequest,
  createForecastRequest,
  deleteForecastRequest,
  getForecastRequest,
  getLatestMatchingForecastRequest,
  listForecastsRequest,
  type ForecastModel,
  type ForecastTarget,
  type ListForecastsParams,
} from "@/api/forecasts";

const FORECASTS_QUERY_KEY = ["forecasts"] as const;

function listKey(params: ListForecastsParams) {
  return [...FORECASTS_QUERY_KEY, "list", params] as const;
}

function detailKey(forecastId: string) {
  return [...FORECASTS_QUERY_KEY, "detail", forecastId] as const;
}

function latestMatchingKey(target: ForecastTarget, forecastModel?: ForecastModel) {
  return [...FORECASTS_QUERY_KEY, "latest-matching", target, forecastModel ?? null] as const;
}

export function useForecastList(params: ListForecastsParams) {
  return useQuery({
    queryKey: listKey(params),
    queryFn: () => listForecastsRequest(params),
  });
}

export function useForecast(forecastId: string, options?: { pollMs?: number; enabled?: boolean }) {
  return useQuery({
    queryKey: detailKey(forecastId),
    queryFn: () => getForecastRequest(forecastId),
    refetchInterval: options?.pollMs,
    enabled: options?.enabled ?? true,
  });
}

export function useLatestMatchingForecast(
  target: ForecastTarget,
  enabled: boolean = true,
  forecastModel?: ForecastModel,
) {
  return useQuery({
    queryKey: latestMatchingKey(target, forecastModel),
    queryFn: () => getLatestMatchingForecastRequest(target, forecastModel),
    enabled,
  });
}

export function useCreateForecast() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createForecastRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FORECASTS_QUERY_KEY });
    },
  });
}

export function useCancelForecast() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (forecastId: string) => cancelForecastRequest(forecastId),
    onSuccess: (updatedJob) => {
      queryClient.invalidateQueries({ queryKey: FORECASTS_QUERY_KEY });
      queryClient.setQueryData(detailKey(updatedJob.id), updatedJob);
    },
  });
}

export function useDeleteForecast() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (forecastId: string) => deleteForecastRequest(forecastId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FORECASTS_QUERY_KEY });
    },
  });
}
