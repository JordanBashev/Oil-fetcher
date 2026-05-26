import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import {
  FORECAST_STATUS,
  TERMINAL_FORECAST_STATUSES,
  createForecastRequest,
  getForecastRequest,
  getLatestMatchingForecastRequest,
  type ForecastJob,
  type ForecastModel,
  type ForecastTarget,
} from "@/api/forecasts";
import { extractErrorMessage } from "@/api/errors";

const POLL_INTERVAL_MS = 2000;
const RUN_FAILED_MESSAGE = "Forecast failed";

type SlotState = {
  job: ForecastJob | null;
  isRunning: boolean;
  errorMessage: string | null;
};

export function useForecastSlot(
  model: ForecastModel,
  target: ForecastTarget,
  isEnabled: boolean,
) {
  const queryClient = useQueryClient();
  const [state, setState] = useState<SlotState>({
    job: null,
    isRunning: false,
    errorMessage: null,
  });

  const targetKey = JSON.stringify(target);

  useEffect(() => {
    if (!isEnabled) return;
    let cancelled = false;

    const loadLatest = async () => {
      try {
        const latest = await getLatestMatchingForecastRequest(target);
        if (cancelled) return;
        if (latest && latest.forecast_model === model) {
          setState({ job: latest, isRunning: false, errorMessage: null });
        } else {
          setState({ job: null, isRunning: false, errorMessage: null });
        }
      } catch {
        if (!cancelled) {
          setState({ job: null, isRunning: false, errorMessage: null });
        }
      }
    };

    loadLatest();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [model, targetKey, isEnabled]);

  useEffect(() => {
    if (!state.job) return;
    if (TERMINAL_FORECAST_STATUSES.includes(state.job.status)) return;
    const jobId = state.job.id;

    let cancelled = false;
    const pollTimer = setInterval(async () => {
      try {
        const updated = await getForecastRequest(jobId);
        if (cancelled) return;
        setState((current) => ({ ...current, job: updated }));
        if (TERMINAL_FORECAST_STATUSES.includes(updated.status)) {
          clearInterval(pollTimer);
          queryClient.invalidateQueries({ queryKey: ["forecasts"] });
          if (updated.status === FORECAST_STATUS.FAILED) {
            setState((current) => ({
              ...current,
              errorMessage: updated.error_message ?? RUN_FAILED_MESSAGE,
              isRunning: false,
            }));
          } else {
            setState((current) => ({ ...current, isRunning: false }));
          }
        }
      } catch {
        /* keep polling */
      }
    }, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      clearInterval(pollTimer);
    };
  }, [state.job, queryClient]);

  const run = async () => {
    setState({ job: null, isRunning: true, errorMessage: null });
    try {
      const existing = await getLatestMatchingForecastRequest(target);
      if (existing && existing.forecast_model === model && existing.is_based_on_latest_data) {
        setState({ job: existing, isRunning: false, errorMessage: null });
        return;
      }
      const createdJob = await createForecastRequest({ forecast_model: model, ...target });
      setState({ job: createdJob, isRunning: true, errorMessage: null });
      queryClient.invalidateQueries({ queryKey: ["forecasts"] });
    } catch (createError) {
      setState({
        job: null,
        isRunning: false,
        errorMessage: extractErrorMessage(createError, "Could not start forecast"),
      });
    }
  };

  return { ...state, run };
}
