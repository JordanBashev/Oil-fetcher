import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Badge,
  Button,
  Card,
  Center,
  Group,
  Loader,
  Radio,
  Select,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import dayjs from "dayjs";

import type { ForecastTarget } from "@/api/forecasts";
import type { OilPriceFilters } from "@/api/oil";
import { HistoryAndForecastChart } from "@/components/forecasts/HistoryAndForecastChart";
import { useLatestMatchingForecast } from "@/hooks/useForecasts";
import { useOilPrices, useOilSeries, useOilUnits } from "@/hooks/useOil";

const TARGET_MODE_AGGREGATE = "aggregate";
const TARGET_MODE_SINGLE = "single";
type TargetMode = typeof TARGET_MODE_AGGREGATE | typeof TARGET_MODE_SINGLE;

const VIEW_PRESET_ALL = "all";
const VIEW_PRESET_1Y = "1y";
const VIEW_PRESET_3M = "3m";
const VIEW_PRESET_3W = "3w";
const VIEW_PRESET_WEEK = "week";

const VIEW_PRESETS = [
  { value: VIEW_PRESET_ALL, label: "All time" },
  { value: VIEW_PRESET_1Y, label: "1 year" },
  { value: VIEW_PRESET_3M, label: "3 months" },
  { value: VIEW_PRESET_3W, label: "3 weeks" },
  { value: VIEW_PRESET_WEEK, label: "This week" },
];

const ISO_DATE_FORMAT = "YYYY-MM-DD";

function presetToDateFrom(preset: string): string | undefined {
  const today = dayjs();
  switch (preset) {
    case VIEW_PRESET_1Y:
      return today.subtract(1, "year").format(ISO_DATE_FORMAT);
    case VIEW_PRESET_3M:
      return today.subtract(3, "month").format(ISO_DATE_FORMAT);
    case VIEW_PRESET_3W:
      return today.subtract(3, "week").format(ISO_DATE_FORMAT);
    case VIEW_PRESET_WEEK:
      return today.startOf("week").format(ISO_DATE_FORMAT);
    default:
      return undefined;
  }
}

export function DashboardPage() {
  const navigate = useNavigate();
  const seriesQuery = useOilSeries();
  const unitsQuery = useOilUnits();

  const [targetMode, setTargetMode] = useState<TargetMode>(TARGET_MODE_AGGREGATE);
  const [selectedSeriesId, setSelectedSeriesId] = useState<string | null>(null);
  const [selectedUnit, setSelectedUnit] = useState<string | null>(null);
  const [viewPreset, setViewPreset] = useState<string>(VIEW_PRESET_1Y);

  useEffect(() => {
    if (selectedUnit === null && unitsQuery.data && unitsQuery.data.length > 0) {
      setSelectedUnit(unitsQuery.data[0]);
    }
  }, [unitsQuery.data, selectedUnit]);

  const target: ForecastTarget = useMemo(() => {
    if (targetMode === TARGET_MODE_SINGLE && selectedSeriesId) {
      return { oil_series_id: selectedSeriesId };
    }
    if (targetMode === TARGET_MODE_AGGREGATE && selectedUnit) {
      return { units: selectedUnit };
    }
    return {};
  }, [targetMode, selectedSeriesId, selectedUnit]);

  const targetReady = Object.keys(target).length > 0;

  const filters: OilPriceFilters = useMemo(() => {
    const built: OilPriceFilters = { ...target };
    const dateFrom = presetToDateFrom(viewPreset);
    if (dateFrom) built.date_from = dateFrom;
    return built;
  }, [target, viewPreset]);

  const pricesQuery = useOilPrices(filters);
  const latestForecastQuery = useLatestMatchingForecast(target, targetReady);
  const latestForecast = latestForecastQuery.data ?? null;

  const seriesOptions = useMemo(
    () =>
      seriesQuery.data?.map((series) => ({ value: series.id, label: series.series_description })) ?? [],
    [seriesQuery.data],
  );

  const unitOptions = useMemo(
    () => unitsQuery.data?.map((unit) => ({ value: unit, label: unit })) ?? [],
    [unitsQuery.data],
  );

  const handleRunForecast = () => {
    navigate("/forecasts/new", { state: { target } });
  };

  return (
    <Stack gap="md">
      <Group justify="space-between">
        <Title order={2}>Dashboard</Title>
        <Button onClick={handleRunForecast} disabled={!targetReady}>
          Run forecast
        </Button>
      </Group>

      <Card withBorder>
        <Stack gap="sm">
          <Radio.Group
            label="Target"
            value={targetMode}
            onChange={(nextValue) => setTargetMode(nextValue as TargetMode)}
          >
            <Group mt="xs">
              <Radio value={TARGET_MODE_AGGREGATE} label="Aggregate" />
              <Radio value={TARGET_MODE_SINGLE} label="Single series" />
            </Group>
          </Radio.Group>

          {targetMode === TARGET_MODE_SINGLE ? (
            <Select
              label="Series"
              placeholder="Pick a series"
              data={seriesOptions}
              value={selectedSeriesId}
              onChange={setSelectedSeriesId}
              searchable
            />
          ) : (
            <Select
              label="Unit"
              data={unitOptions}
              value={selectedUnit}
              onChange={setSelectedUnit}
            />
          )}

          <Select
            label="View period"
            data={VIEW_PRESETS}
            value={viewPreset}
            onChange={(nextValue) => nextValue && setViewPreset(nextValue)}
          />
        </Stack>
      </Card>

      <Card withBorder>
        {pricesQuery.isLoading ? (
          <Center h={300}>
            <Loader />
          </Center>
        ) : pricesQuery.isError ? (
          <Text c="red">Failed to load oil prices.</Text>
        ) : (
          <Stack gap="sm">
            <Group gap="xs">
              <Badge color={pricesQuery.data?.is_aggregated ? "blue" : "gray"}>
                {pricesQuery.data?.is_aggregated ? "Aggregate" : "Single series"}
              </Badge>
              {pricesQuery.data?.unit_label && (
                <Text size="sm" c="dimmed">{pricesQuery.data.unit_label}</Text>
              )}
              {latestForecast && (
                <Badge color="grape" variant="light">Forecast overlay</Badge>
              )}
              {!latestForecast && targetReady && !latestForecastQuery.isLoading && (
                <Text size="sm" c="dimmed">No forecast yet for this target.</Text>
              )}
            </Group>
            <HistoryAndForecastChart
              history={pricesQuery.data?.series ?? []}
              forecast={latestForecast}
              unitLabel={pricesQuery.data?.unit_label ?? null}
            />
          </Stack>
        )}
      </Card>
    </Stack>
  );
}
