import { useState } from "react";
import {
  Badge,
  Card,
  Center,
  Group,
  Loader,
  Pagination,
  Select,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import dayjs from "dayjs";

import type { LogFilters } from "@/api/admin";
import { useAdminLogs } from "@/hooks/useAdmin";

const PAGE_SIZE = 50;
const TIMESTAMP_FORMAT = "YYYY-MM-DD HH:mm:ss";

const LEVEL_OPTIONS = [
  { value: "", label: "Any" },
  { value: "DEBUG", label: "DEBUG" },
  { value: "INFO", label: "INFO" },
  { value: "WARNING", label: "WARNING" },
  { value: "ERROR", label: "ERROR" },
  { value: "CRITICAL", label: "CRITICAL" },
];

const LEVEL_COLORS: Record<string, string> = {
  DEBUG: "gray",
  INFO: "blue",
  WARNING: "yellow",
  ERROR: "red",
  CRITICAL: "red",
};

function formatTimestamp(isoString: string): string {
  return dayjs(isoString).format(TIMESTAMP_FORMAT);
}

export function AdminLogsPage() {
  const [filters, setFilters] = useState<LogFilters>({});
  const [currentPage, setCurrentPage] = useState(1);

  const logsQuery = useAdminLogs({ ...filters, page: currentPage, items_per_page: PAGE_SIZE });

  const updateFilter = (key: keyof LogFilters, value: string | undefined) => {
    setFilters((current) => ({ ...current, [key]: value || undefined }));
    setCurrentPage(1);
  };

  return (
    <Stack gap="md">
      <Title order={2}>Logs</Title>

      <Card withBorder>
        <Group align="end" gap="sm" wrap="wrap">
          <Select
            label="Level"
            data={LEVEL_OPTIONS}
            value={filters.level ?? ""}
            onChange={(nextValue) => updateFilter("level", nextValue ?? "")}
            w={140}
          />
          <TextInput
            label="Logger"
            value={filters.logger ?? ""}
            onChange={(changeEvent) => updateFilter("logger", changeEvent.currentTarget.value)}
            placeholder="substring"
            w={200}
          />
          <TextInput
            label="Search"
            value={filters.search ?? ""}
            onChange={(changeEvent) => updateFilter("search", changeEvent.currentTarget.value)}
            placeholder="substring"
            w={240}
          />
          <TextInput
            label="From"
            type="date"
            value={filters.date_from ?? ""}
            onChange={(changeEvent) => updateFilter("date_from", changeEvent.currentTarget.value)}
          />
          <TextInput
            label="To"
            type="date"
            value={filters.date_to ?? ""}
            onChange={(changeEvent) => updateFilter("date_to", changeEvent.currentTarget.value)}
          />
        </Group>
      </Card>

      <Card withBorder>
        {logsQuery.isLoading ? (
          <Center h={200}>
            <Loader />
          </Center>
        ) : logsQuery.isError ? (
          <Text c="red">Failed to load logs.</Text>
        ) : logsQuery.data && logsQuery.data.items.length === 0 ? (
          <Text c="dimmed">No log lines match the filters.</Text>
        ) : (
          <Stack gap="sm">
            <Table verticalSpacing="xs">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Time</Table.Th>
                  <Table.Th>Level</Table.Th>
                  <Table.Th>Logger</Table.Th>
                  <Table.Th>Message</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {logsQuery.data?.items.map((line, lineIndex) => (
                  <Table.Tr key={`${line.timestamp}-${lineIndex}`}>
                    <Table.Td>{formatTimestamp(line.timestamp)}</Table.Td>
                    <Table.Td>
                      <Badge color={LEVEL_COLORS[line.level] ?? "gray"} variant="light">
                        {line.level}
                      </Badge>
                    </Table.Td>
                    <Table.Td>{line.logger}</Table.Td>
                    <Table.Td>
                      <Text size="sm" style={{ fontFamily: "monospace", whiteSpace: "pre-wrap" }}>
                        {line.message}
                      </Text>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
            {logsQuery.data && (
              <Group justify="space-between">
                <Text size="sm" c="dimmed">
                  {logsQuery.data.pagination.total_count} total
                </Text>
                <Pagination
                  value={currentPage}
                  onChange={setCurrentPage}
                  total={logsQuery.data.pagination.total_pages}
                />
              </Group>
            )}
          </Stack>
        )}
      </Card>
    </Stack>
  );
}
