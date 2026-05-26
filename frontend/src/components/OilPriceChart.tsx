import { Text } from "@mantine/core";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { OilPriceSeries } from "@/api/oil";

const CHART_HEIGHT = 380;
const SERIES_COLORS = [
  "#1f77b4",
  "#ff7f0e",
  "#2ca02c",
  "#d62728",
  "#9467bd",
  "#8c564b",
  "#e377c2",
];
const DOT_RADIUS = 2;
const ACTIVE_DOT_RADIUS = 5;

type ChartRow = { period: string } & Record<string, number | string>;

type OilPriceChartProps = {
  series: OilPriceSeries[];
  unitLabel: string | null;
};

function buildChartRows(series: OilPriceSeries[]): ChartRow[] {
  const periodToRow = new Map<string, ChartRow>();
  for (const oneSeries of series) {
    for (const point of oneSeries.points) {
      const existingRow = periodToRow.get(point.period) ?? { period: point.period };
      existingRow[oneSeries.series_code] = point.value;
      periodToRow.set(point.period, existingRow);
    }
  }
  return Array.from(periodToRow.values()).sort((rowA, rowB) =>
    rowA.period.localeCompare(rowB.period),
  );
}

export function OilPriceChart({ series, unitLabel }: OilPriceChartProps) {
  if (series.length === 0) {
    return <Text c="dimmed">No data for the selected filters.</Text>;
  }

  const rows = buildChartRows(series);
  const yAxisLabel = unitLabel ?? "Price";

  return (
    <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
      <LineChart data={rows} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="period" />
        <YAxis label={{ value: yAxisLabel, angle: -90, position: "insideLeft" }} />
        <Tooltip />
        <Legend />
        {series.map((oneSeries, seriesIndex) => (
          <Line
            key={oneSeries.series_code}
            type="monotone"
            dataKey={oneSeries.series_code}
            name={oneSeries.series_description}
            stroke={SERIES_COLORS[seriesIndex % SERIES_COLORS.length]}
            dot={{ r: DOT_RADIUS }}
            activeDot={{ r: ACTIVE_DOT_RADIUS }}
            connectNulls
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
