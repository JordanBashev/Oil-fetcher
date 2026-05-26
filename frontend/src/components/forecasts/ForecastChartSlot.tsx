import { Box, Button, Card, Center, Group, Stack, Text } from "@mantine/core";

import type { ForecastJob } from "@/api/forecasts";
import { ForecastStatusBadge } from "@/components/forecasts/ForecastStatusBadge";
import { HistoryAndForecastChart } from "@/components/forecasts/HistoryAndForecastChart";
import type { OilPriceSeries } from "@/api/oil";

type ForecastChartSlotProps = {
  title: string;
  job: ForecastJob | null;
  history: OilPriceSeries[];
  isHistoryLoading: boolean;
  isJobLoading: boolean;
  errorMessage: string | null;
  onRetry: () => void;
  unitLabel: string | null;
};

export function ForecastChartSlot({
  title,
  job,
  history,
  isHistoryLoading,
  isJobLoading,
  errorMessage,
  onRetry,
  unitLabel,
}: ForecastChartSlotProps) {
  const showLoadingOverlay = isJobLoading;

  return (
    <Card withBorder>
      <Stack gap="sm">
        <Group justify="space-between">
          <Text fw={500}>{title}</Text>
          {job && <ForecastStatusBadge status={job.status} />}
        </Group>

        {errorMessage ? (
          <Center h={280}>
            <Stack align="center" gap="sm">
              <Text c="red">Something went wrong.</Text>
              <Text size="sm" c="dimmed">{errorMessage}</Text>
              <Button variant="default" onClick={onRetry}>Try again</Button>
            </Stack>
          </Center>
        ) : showLoadingOverlay && !job ? (
          <Center h={280}>
            <Text c="dimmed">Running forecast…</Text>
          </Center>
        ) : (
          <Box>
            <HistoryAndForecastChart
              history={history}
              forecast={job}
              isLoading={isHistoryLoading && !job}
              unitLabel={unitLabel}
            />
          </Box>
        )}
      </Stack>
    </Card>
  );
}
