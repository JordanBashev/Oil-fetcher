import { AxiosError } from "axios";

const DEFAULT_ERROR_MESSAGE = "Something went wrong";

export function extractErrorMessage(error: unknown, fallback: string = DEFAULT_ERROR_MESSAGE): string {
  if (!(error instanceof AxiosError)) {
    return fallback;
  }
  const detail = error.response?.data?.detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail) && detail.length > 0 && typeof detail[0]?.msg === "string") {
    return detail[0].msg;
  }
  return fallback;
}
