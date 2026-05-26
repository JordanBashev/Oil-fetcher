import { Badge } from "@mantine/core";

import { FORECAST_STATUS, type ForecastStatus } from "@/api/forecasts";

const STATUS_COLORS: Record<ForecastStatus, string> = {
  [FORECAST_STATUS.PENDING]: "gray",
  [FORECAST_STATUS.PROCESSING]: "blue",
  [FORECAST_STATUS.COMPLETED]: "green",
  [FORECAST_STATUS.FAILED]: "red",
  [FORECAST_STATUS.CANCELED]: "yellow",
};

type ForecastStatusBadgeProps = { status: ForecastStatus };

export function ForecastStatusBadge({ status }: ForecastStatusBadgeProps) {
  return <Badge color={STATUS_COLORS[status]}>{status}</Badge>;
}
