import { useState } from "react";
import {
  ActionIcon,
  Badge,
  Button,
  Card,
  Center,
  Group,
  Loader,
  Modal,
  Select,
  Stack,
  Switch,
  Table,
  Text,
  Title,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import dayjs from "dayjs";

import type { AdminUser, Role } from "@/api/admin";
import { extractErrorMessage } from "@/api/errors";
import {
  useAdminRoles,
  useAdminUsers,
  useAssignRole,
  useDeleteAdminUser,
  useRemoveRole,
  useSetUserStatus,
} from "@/hooks/useAdmin";

const DATE_DISPLAY_FORMAT = "YYYY-MM-DD";

function formatDate(isoString: string): string {
  return dayjs(isoString).format(DATE_DISPLAY_FORMAT);
}

type AssignRoleModalProps = {
  user: AdminUser | null;
  roles: Role[];
  onClose: () => void;
  onConfirm: (roleId: string) => void;
  isPending: boolean;
};

function AssignRoleModal({ user, roles, onClose, onConfirm, isPending }: AssignRoleModalProps) {
  const [selectedRoleId, setSelectedRoleId] = useState<string | null>(null);
  const assignableRoles = user
    ? roles.filter((role) => !user.roles.includes(role.name))
    : [];

  return (
    <Modal opened={user !== null} onClose={onClose} title="Assign role" size="sm">
      {user && (
        <Stack gap="sm">
          <Text size="sm" c="dimmed">{user.email}</Text>
          <Select
            label="Role"
            data={assignableRoles.map((role) => ({ value: role.id, label: role.name }))}
            value={selectedRoleId}
            onChange={setSelectedRoleId}
            placeholder={assignableRoles.length === 0 ? "All roles already assigned" : "Pick a role"}
            disabled={assignableRoles.length === 0}
          />
          <Group justify="flex-end">
            <Button variant="default" onClick={onClose}>Cancel</Button>
            <Button
              onClick={() => selectedRoleId && onConfirm(selectedRoleId)}
              disabled={!selectedRoleId}
              loading={isPending}
            >
              Assign
            </Button>
          </Group>
        </Stack>
      )}
    </Modal>
  );
}

export function AdminUsersPage() {
  const usersQuery = useAdminUsers();
  const rolesQuery = useAdminRoles();
  const setUserStatus = useSetUserStatus();
  const deleteUser = useDeleteAdminUser();
  const assignRole = useAssignRole();
  const removeRole = useRemoveRole();

  const [assignTargetUser, setAssignTargetUser] = useState<AdminUser | null>(null);

  const handleToggleActive = async (user: AdminUser) => {
    try {
      await setUserStatus.mutateAsync({
        userId: user.id,
        body: { is_active: !user.is_active },
      });
      notifications.show({ color: "green", message: "Status updated" });
    } catch (statusError) {
      notifications.show({
        color: "red",
        message: extractErrorMessage(statusError, "Status update failed"),
      });
    }
  };

  const handleDelete = async (user: AdminUser) => {
    try {
      await deleteUser.mutateAsync(user.id);
      notifications.show({ color: "green", message: "User deleted" });
    } catch (deleteError) {
      notifications.show({
        color: "red",
        message: extractErrorMessage(deleteError, "Delete failed"),
      });
    }
  };

  const handleAssignRole = async (roleId: string) => {
    if (!assignTargetUser) return;
    try {
      await assignRole.mutateAsync({ userId: assignTargetUser.id, body: { role_id: roleId } });
      notifications.show({ color: "green", message: "Role assigned" });
      setAssignTargetUser(null);
    } catch (assignError) {
      notifications.show({
        color: "red",
        message: extractErrorMessage(assignError, "Assign failed"),
      });
    }
  };

  const handleRemoveRole = async (user: AdminUser, roleName: string) => {
    const role = rolesQuery.data?.find((candidateRole) => candidateRole.name === roleName);
    if (!role) return;
    try {
      await removeRole.mutateAsync({ userId: user.id, roleId: role.id });
      notifications.show({ color: "green", message: "Role removed" });
    } catch (removeError) {
      notifications.show({
        color: "red",
        message: extractErrorMessage(removeError, "Remove failed"),
      });
    }
  };

  return (
    <Stack gap="md">
      <Title order={2}>Users</Title>

      <Card withBorder>
        {usersQuery.isLoading && (
          <Center h={200}>
            <Loader />
          </Center>
        )}
        {usersQuery.isError && <Text c="red">Failed to load users.</Text>}
        {usersQuery.data && (
          <Table verticalSpacing="xs">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Email</Table.Th>
                <Table.Th>Created</Table.Th>
                <Table.Th>Active</Table.Th>
                <Table.Th>Roles</Table.Th>
                <Table.Th>Actions</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {usersQuery.data.map((user) => (
                <Table.Tr key={user.id}>
                  <Table.Td>{user.email}</Table.Td>
                  <Table.Td>{formatDate(user.created_at)}</Table.Td>
                  <Table.Td>
                    <Switch
                      checked={user.is_active}
                      onChange={() => handleToggleActive(user)}
                      disabled={setUserStatus.isPending}
                    />
                  </Table.Td>
                  <Table.Td>
                    <Group gap="xs">
                      {user.roles.map((roleName) => (
                        <Badge
                          key={roleName}
                          variant="light"
                          rightSection={
                            <ActionIcon
                              size="xs"
                              variant="transparent"
                              onClick={() => handleRemoveRole(user, roleName)}
                              aria-label={`Remove ${roleName}`}
                            >
                              ✕
                            </ActionIcon>
                          }
                        >
                          {roleName}
                        </Badge>
                      ))}
                    </Group>
                  </Table.Td>
                  <Table.Td>
                    <Group gap="xs">
                      <Button
                        size="xs"
                        variant="default"
                        onClick={() => setAssignTargetUser(user)}
                      >
                        Assign role
                      </Button>
                      <ActionIcon
                        color="red"
                        variant="subtle"
                        onClick={() => handleDelete(user)}
                        loading={deleteUser.isPending}
                        aria-label="Delete user"
                      >
                        ✕
                      </ActionIcon>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        )}
      </Card>

      <AssignRoleModal
        user={assignTargetUser}
        roles={rolesQuery.data ?? []}
        onClose={() => setAssignTargetUser(null)}
        onConfirm={handleAssignRole}
        isPending={assignRole.isPending}
      />
    </Stack>
  );
}
