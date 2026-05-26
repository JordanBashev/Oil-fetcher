import { useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";
import {
  Button,
  Card,
  Checkbox,
  Group,
  Radio,
  Select,
  Stack,
  Text,
  Title,
} from "@mantine/core";

import { FORECAST_MODEL, type ForecastModel, type ForecastTarget } from "@/api/forecasts";
import { ForecastChartSlot } from "@/components/forecasts/ForecastChartSlot";
import { useForecastSlot } from "@/hooks/useForecastSlot";
import { useOilPrices, useOilSeries, useOilUnits } from "@/hooks/useOil";

const TARGET_MODE_SINGLE = "single";
const TARGET_MODE_AGGREGATE = "aggregate";
type TargetMode = typeof TARGET_MODE_SINGLE | typeof TARGET_MODE_AGGREGATE;

const MODEL_OPTIONS = [
  { value: FORECAST_MODEL.HOLT_WINTERS_V1, label: "Holt-Winters" },
  { value: FORECAST_MODEL.LINEAR_REGRESSION_V1, label: "Linear Regression" },
];

function otherModel(model: ForecastModel): ForecastModel {
  return model === FORECAST_MODEL.HOLT_WINTERS_V1
    ? FORECAST_MODEL.LINEAR_REGRESSION_V1
    : FORECAST_MODEL.HOLT_WINTERS_V1;
}

function buildTarget(mode: TargetMode, seriesId: string | null, unit: string | null): ForecastTarget | null {
  if (mode === TARGET_MODE_SINGLE) {
    return seriesId ? { oil_series_id: seriesId } : null;
  }
  return unit ? { units: unit } : null;
}

export function NewForecastPage() {
  const location = useLocation();
  const prefilledTarget = (location.state as { target?: ForecastTarget } | null)?.target;

  const seriesQuery = useOilSeries();
  const unitsQuery = useOilUnits();

  const initialMode: TargetMode = prefilledTarget?.oil_series_id ? TARGET_MODE_SINGLE : TARGET_MODE_AGGREGATE;
  const [targetMode, setTargetMode] = useState<TargetMode>(initialMode);
  const [selectedSeriesId, setSelectedSeriesId] = useState<string | null>(
    prefilledTarget?.oil_series_id ?? null,
  );
  const [selectedUnit, setSelectedUnit] = useState<string | null>(prefilledTarget?.units ?? null);
  const [topModel, setTopModel] = useState<ForecastModel>(FORECAST_MODEL.HOLT_WINTERS_V1);
  const [compareEnabled, setCompareEnabled] = useState(false);

  useEffect(() => {
    if (selectedUnit === null && unitsQuery.data && unitsQuery.data.length > 0) {
      setSelectedUnit(unitsQuery.data[0]);
    }
  }, [unitsQuery.data, selectedUnit]);

  useEffect(() => {
    if (selectedSeriesId === null && seriesQuery.data && seriesQuery.data.length > 0) {
      setSelectedSeriesId(seriesQuery.data[0].id);
    }
  }, [seriesQuery.data, selectedSeriesId]);

  const target = buildTarget(targetMode, selectedSeriesId, selectedUnit);
  const targetReady = target !== null;

  const bottomModel = otherModel(topModel);
  const topSlot = useForecastSlot(topModel, target ?? {}, targetReady);
  const bottomSlot = useForecastSlot(bottomModel, target ?? {}, targetReady && compareEnabled);

  const pricesQuery = useOilPrices(target ?? {});
  const history = pricesQuery.data?.series ?? [];
  const unitLabel = pricesQuery.data?.unit_label ?? null;

  const seriesOptions = useMemo(
    () =>
      seriesQuery.data?.map((series) => ({ value: series.id, label: series.series_description })) ?? [],
    [seriesQuery.data],
  );

  const unitOptions = useMemo(
    () => unitsQuery.data?.map((unit) => ({ value: unit, label: unit })) ?? [],
    [unitsQuery.data],
  );

  const handleRun = () => {
    topSlot.run();
    if (compareEnabled) bottomSlot.run();
  };

  const isAnyRunning = topSlot.isRunning || bottomSlot.isRunning;

  return (
    <Stack gap="md">
      <Title order={2}>New forecast</Title>

      <Card withBorder>
        <Stack gap="md">
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
            label="Model"
            data={MODEL_OPTIONS}
            value={topModel}
            onChange={(nextValue) => nextValue && setTopModel(nextValue as ForecastModel)}
          />

          <Checkbox
            label="Compare with the other model"
            checked={compareEnabled}
            onChange={(changeEvent) => setCompareEnabled(changeEvent.currentTarget.checked)}
          />

          <Group>
            <Button onClick={handleRun} disabled={!targetReady} loading={isAnyRunning}>
              Run forecast
            </Button>
            {!targetReady && <Text size="sm" c="dimmed">Pick a target first.</Text>}
          </Group>
        </Stack>
      </Card>

      <ForecastChartSlot
        title={topModel === FORECAST_MODEL.HOLT_WINTERS_V1 ? "Holt-Winters" : "Linear Regression"}
        job={topSlot.job}
        history={history}
        isHistoryLoading={pricesQuery.isLoading}
        isJobLoading={topSlot.isRunning}
        errorMessage={topSlot.errorMessage}
        onRetry={topSlot.run}
        unitLabel={unitLabel}
      />

      {compareEnabled && (
        <ForecastChartSlot
          title={bottomModel === FORECAST_MODEL.HOLT_WINTERS_V1 ? "Holt-Winters" : "Linear Regression"}
          job={bottomSlot.job}
          history={history}
          isHistoryLoading={pricesQuery.isLoading}
          isJobLoading={bottomSlot.isRunning}
          errorMessage={bottomSlot.errorMessage}
          onRetry={bottomSlot.run}
          unitLabel={unitLabel}
        />
      )}
    </Stack>
  );
}
