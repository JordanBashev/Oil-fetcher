import axios, { AxiosError, type AxiosRequestConfig } from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";
const REFRESH_PATH = "/auth/refresh";
const UNAUTHORIZED_STATUS = 401;

type RetryableConfig = AxiosRequestConfig & { _retried?: boolean };

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

type SessionInvalidationListener = () => void;
const sessionInvalidationListeners = new Set<SessionInvalidationListener>();

export function onSessionInvalidated(listener: SessionInvalidationListener): () => void {
  sessionInvalidationListeners.add(listener);
  return () => sessionInvalidationListeners.delete(listener);
}

function notifySessionInvalidated(): void {
  sessionInvalidationListeners.forEach((listener) => listener());
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableConfig | undefined;
    const status = error.response?.status;
    const requestUrl = originalRequest?.url ?? "";

    if (
      status === UNAUTHORIZED_STATUS &&
      originalRequest &&
      !originalRequest._retried &&
      !requestUrl.endsWith(REFRESH_PATH)
    ) {
      originalRequest._retried = true;
      try {
        await apiClient.post(REFRESH_PATH);
        return apiClient.request(originalRequest);
      } catch (refreshError) {
        notifySessionInvalidated();
        return Promise.reject(refreshError);
      }
    }

    if (status === UNAUTHORIZED_STATUS && requestUrl.endsWith(REFRESH_PATH)) {
      notifySessionInvalidated();
    }

    return Promise.reject(error);
  },
);
