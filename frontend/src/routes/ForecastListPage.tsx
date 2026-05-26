import { Fragment, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ActionIcon,
  Badge,
  Box,
  Button,
  Card,
  Center,
  Collapse,
  Group,
  Loader,
  Pagination,
  Stack,
  Table,
  Text,
  Title,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import dayjs from "dayjs";

import { FORECAST_STATUS, type ForecastJob } from "@/api/forecasts";
import { extractErrorMessage } from "@/api/errors";
import { ForecastStatusBadge } from "@/components/forecasts/ForecastStatusBadge";
import { HistoryAndForecastChart } from "@/components/forecasts/HistoryAndForecastChart";
import {
  describeForecastTarget,
  jobToTarget,
} from "@/components/forecasts/forecastTarget";
import {
  useCancelForecast,
  useDeleteForecast,
  useForecastList,
} from "@/hooks/useForecasts";
import { useOilPrices, useOilSeries } from "@/hooks/useOil";

const PAGE_SIZE = 20;
const DATE_DISPLAY_FORMAT = "YYYY-MM-DD HH:mm";

function formatTimestamp(isoString: string): string {
  return dayjs(isoString).format(DATE_DISPLAY_FORMAT);
}

function ExpandedChart({ job }: { job: ForecastJob }) {
  const seriesQuery = useOilSeries();
  const pricesQuery = useOilPrices(jobToTarget(job));

  const seriesById = seriesQuery.data
    ? new Map(seriesQuery.data.map((series) => [series.id, series]))
    : undefined;

  return (
    <Stack gap="xs" mt="sm">
      <Text size="sm" c="dimmed">
        {describeForecastTarget(job, seriesById)}
      </Text>
      <HistoryAndForecastChart
        history={pricesQuery.data?.series ?? []}
        forecast={job}
        isLoading={pricesQuery.isLoading}
        unitLabel={pricesQuery.data?.unit_label ?? null}
      />
    </Stack>
  );
}

export function ForecastListPage() {
  const [currentPage, setCurrentPage] = useState(1);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const listQuery = useForecastList({ page: currentPage, items_per_page: PAGE_SIZE });
  const seriesQuery = useOilSeries();
  const cancelForecast = useCancelForecast();
  const deleteForecast = useDeleteForecast();
  const navigate = useNavigate();

  const seriesById = seriesQuery.data
    ? new Map(seriesQuery.data.map((series) => [series.id, series]))
    : undefined;

  const handleCancel = async (forecastId: string) => {
    try {
      await cancelForecast.mutateAsync(forecastId);
      notifications.show({ color: "green", message: "Forecast canceled" });
    } catch (cancelError) {
      notifications.show({
        color: "red",
        message: extractErrorMessage(cancelError, "Cancel failed"),
      });
    }
  };

  const handleDelete = async (forecastId: string) => {
    try {
      await deleteForecast.mutateAsync(forecastId);
      notifications.show({ color: "green", message: "Forecast deleted" });
      if (expandedId === forecastId) setExpandedId(null);
    } catch (deleteError) {
      notifications.show({
        color: "red",
        message: extractErrorMessage(deleteError, "Delete failed"),
      });
    }
  };

  const toggleExpanded = (forecastId: string) => {
    setExpandedId((current) => (current === forecastId ? null : forecastId));
  };

  return (
    <Stack gap="md">
      <Group justify="space-between">
        <Title order={2}>Forecasts</Title>
        <Group>
          <Button variant="default" onClick={() => listQuery.refetch()} loading={listQuery.isFetching}>
            Refresh
          </Button>
          <Button onClick={() => navigate("/forecasts/new")}>New forecast</Button>
        </Group>
      </Group>

      <Card withBorder>
        {listQuery.isLoading && (
          <Center h={200}>
            <Loader />
          </Center>
        )}
        {listQuery.isError && <Text c="red">Failed to load forecasts.</Text>}
        {listQuery.data && listQuery.data.items.length === 0 && (
          <Text c="dimmed">No forecasts yet.</Text>
        )}
        {listQuery.data && listQuery.data.items.length > 0 && (
          <Stack gap="sm">
            <Table verticalSpacing="xs">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Created</Table.Th>
                  <Table.Th>Model</Table.Th>
                  <Table.Th>Target</Table.Th>
                  <Table.Th>Status</Table.Th>
                  <Table.Th>Data</Table.Th>
                  <Table.Th>Actions</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {listQuery.data.items.map((job) => (
                  <Fragment key={job.id}>
                    <Table.Tr>
                      <Table.Td>{formatTimestamp(job.created_at)}</Table.Td>
                      <Table.Td>{job.forecast_model}</Table.Td>
                      <Table.Td>{describeForecastTarget(job, seriesById)}</Table.Td>
                      <Table.Td><ForecastStatusBadge status={job.status} /></Table.Td>
                      <Table.Td>
                        {job.is_based_on_latest_data ? (
                          <Badge color="green" variant="light">Up to date</Badge>
                        ) : (
                          <Badge color="orange" variant="light">Newer data</Badge>
                        )}
                      </Table.Td>
                      <Table.Td>
                        <Group gap="xs">
                          {job.status === FORECAST_STATUS.COMPLETED && (
                            <Button
                              size="xs"
                              variant="default"
                              onClick={() => toggleExpanded(job.id)}
                            >
                              {expandedId === job.id ? "Hide" : "Chart"}
                            </Button>
                          )}
                          {job.status === FORECAST_STATUS.PENDING && (
                            <Button
                              size="xs"
                              variant="default"
                              onClick={() => handleCancel(job.id)}
                              loading={cancelForecast.isPending}
                            >
                              Cancel
                            </Button>
                          )}
                          <ActionIcon
                            color="red"
                            variant="subtle"
                            onClick={() => handleDelete(job.id)}
                            loading={deleteForecast.isPending}
                            aria-label="Delete forecast"
                          >
                            ✕
                          </ActionIcon>
                        </Group>
                      </Table.Td>
                    </Table.Tr>
                    <Table.Tr>
                      <Table.Td colSpan={6} p={0} style={{ borderTop: "none" }}>
                        <Collapse expanded={expandedId === job.id}>
                          <Box p="sm">
                            {expandedId === job.id && <ExpandedChart job={job} />}
                          </Box>
                        </Collapse>
                      </Table.Td>
                    </Table.Tr>
                  </Fragment>
                ))}
              </Table.Tbody>
            </Table>
            <Group justify="space-between">
              <Text size="sm" c="dimmed">
                {listQuery.data.pagination.total_count} total
              </Text>
              <Pagination
                value={currentPage}
                onChange={setCurrentPage}
                total={listQuery.data.pagination.total_pages}
              />
            </Group>
          </Stack>
        )}
      </Card>
    </Stack>
  );
}
