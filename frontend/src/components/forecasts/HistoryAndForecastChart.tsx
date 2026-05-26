import { useMemo } from "react";
import { Center, Loader, Text } from "@mantine/core";
import dayjs from "dayjs";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { ForecastJob, ForecastPoint } from "@/api/forecasts";
import type { OilPriceSeries } from "@/api/oil";

const CHART_HEIGHT = 420;
const HISTORY_COLOR = "#1f77b4";
const FORECAST_COLOR = "#d62728";
const FORECAST_AREA_FILL = "#d62728";
const FORECAST_AREA_OPACITY = 0.08;
const REFERENCE_LINE_COLOR = "#94a3b8";
const DOT_RADIUS = 2;
const ACTIVE_DOT_RADIUS = 5;
const HISTORY_KEY = "history";
const FORECAST_KEY = "forecast";
const X_AXIS_LABEL_FORMAT = "MMM 'YY";
const TOOLTIP_LABEL_FORMAT = "YYYY-MM-DD";

type ChartRow = {
  period: string;
  periodMs: number;
  [HISTORY_KEY]?: number;
  [FORECAST_KEY]?: number;
};

type HistoryAndForecastChartProps = {
  history: OilPriceSeries[];
  forecast: ForecastJob | null;
  isLoading?: boolean;
  unitLabel?: string | null;
};

function buildRows(
  history: OilPriceSeries[],
  forecastPoints: ForecastPoint[],
): { rows: ChartRow[]; boundaryMs: number | null } {
  const periodToRow = new Map<string, ChartRow>();

  const firstHistorySeries = history[0];
  let lastHistoryPeriod: string | null = null;
  let lastHistoryValue: number | null = null;

  if (firstHistorySeries) {
    for (const point of firstHistorySeries.points) {
      const periodMs = dayjs(point.period).valueOf();
      periodToRow.set(point.period, {
        period: point.period,
        periodMs,
        [HISTORY_KEY]: point.value,
      });
      if (lastHistoryPeriod === null || point.period > lastHistoryPeriod) {
        lastHistoryPeriod = point.period;
        lastHistoryValue = point.value;
      }
    }
  }

  if (forecastPoints.length > 0 && lastHistoryPeriod !== null && lastHistoryValue !== null) {
    const row = periodToRow.get(lastHistoryPeriod);
    if (row) row[FORECAST_KEY] = lastHistoryValue;
  }

  for (const forecastPoint of forecastPoints) {
    const periodMs = dayjs(forecastPoint.period).valueOf();
    const existingRow = periodToRow.get(forecastPoint.period) ?? {
      period: forecastPoint.period,
      periodMs,
    };
    existingRow[FORECAST_KEY] = forecastPoint.value;
    periodToRow.set(forecastPoint.period, existingRow);
  }

  const rows = Array.from(periodToRow.values()).sort(
    (rowA, rowB) => rowA.periodMs - rowB.periodMs,
  );
  const boundaryMs = lastHistoryPeriod !== null ? dayjs(lastHistoryPeriod).valueOf() : null;
  return { rows, boundaryMs };
}

function formatXAxisTick(periodMs: unknown): string {
  return dayjs(Number(periodMs)).format(X_AXIS_LABEL_FORMAT);
}

function formatTooltipLabel(periodMs: unknown): string {
  return dayjs(Number(periodMs)).format(TOOLTIP_LABEL_FORMAT);
}

function formatValue(value: unknown): string {
  return typeof value === "number" ? value.toFixed(2) : String(value ?? "");
}

export function HistoryAndForecastChart({
  history,
  forecast,
  isLoading,
  unitLabel,
}: HistoryAndForecastChartProps) {
  const { rows, boundaryMs } = useMemo(
    () => buildRows(history, forecast?.points ?? []),
    [history, forecast],
  );

  if (isLoading) {
    return (
      <Center h={CHART_HEIGHT}>
        <Loader />
      </Center>
    );
  }

  if (rows.length === 0) {
    return <Text c="dimmed">No data to display.</Text>;
  }

  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <ComposedChart data={rows} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="periodMs"
          type="number"
          scale="time"
          domain={["dataMin", "dataMax"]}
          tickFormatter={formatXAxisTick}
          minTickGap={40}
        />
        <YAxis
          label={{ value: unitLabel ?? "Price", angle: -90, position: "insideLeft" }}
          tickFormatter={formatValue}
          domain={["auto", "auto"]}
        />
        <Tooltip labelFormatter={formatTooltipLabel} formatter={formatValue} />
        <Legend />
        {boundaryMs !== null && forecast && (
          <ReferenceLine
            x={boundaryMs}
            stroke={REFERENCE_LINE_COLOR}
            strokeDasharray="2 4"
            label={{ value: "now", position: "top", fill: REFERENCE_LINE_COLOR, fontSize: 12 }}
          />
        )}
        <Area
          type="monotone"
          dataKey={FORECAST_KEY}
          name="Forecast"
          stroke="none"
          fill={FORECAST_AREA_FILL}
          fillOpacity={FORECAST_AREA_OPACITY}
          isAnimationActive={false}
          connectNulls
          legendType="none"
        />
        <Line
          type="monotone"
          dataKey={HISTORY_KEY}
          name="History"
          stroke={HISTORY_COLOR}
          strokeWidth={2}
          dot={{ r: DOT_RADIUS }}
          activeDot={{ r: ACTIVE_DOT_RADIUS }}
          connectNulls
        />
        <Line
          type="monotone"
          dataKey={FORECAST_KEY}
          name="Forecast"
          stroke={FORECAST_COLOR}
          strokeWidth={2}
          strokeDasharray="6 4"
          dot={{ r: DOT_RADIUS, fill: FORECAST_COLOR, stroke: FORECAST_COLOR }}
          activeDot={{ r: ACTIVE_DOT_RADIUS, fill: FORECAST_COLOR, stroke: FORECAST_COLOR }}
          connectNulls
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
