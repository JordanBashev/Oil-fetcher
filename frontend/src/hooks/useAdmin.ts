import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  assignRoleRequest,
  deleteAdminUserRequest,
  listAdminLogsRequest,
  listAdminRolesRequest,
  listAdminUsersRequest,
  removeRoleRequest,
  setUserStatusRequest,
  type AssignRoleBody,
  type ListLogsParams,
  type UserStatusBody,
} from "@/api/admin";

const ADMIN_USERS_QUERY_KEY = ["admin", "users"] as const;
const ADMIN_ROLES_QUERY_KEY = ["admin", "roles"] as const;
const ADMIN_LOGS_QUERY_KEY_PREFIX = ["admin", "logs"] as const;

export function useAdminUsers() {
  return useQuery({
    queryKey: ADMIN_USERS_QUERY_KEY,
    queryFn: listAdminUsersRequest,
  });
}

export function useAdminRoles() {
  return useQuery({
    queryKey: ADMIN_ROLES_QUERY_KEY,
    queryFn: listAdminRolesRequest,
  });
}

export function useDeleteAdminUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) => deleteAdminUserRequest(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ADMIN_USERS_QUERY_KEY });
    },
  });
}

export function useSetUserStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: { userId: string; body: UserStatusBody }) =>
      setUserStatusRequest(input.userId, input.body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ADMIN_USERS_QUERY_KEY });
    },
  });
}

export function useAssignRole() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: { userId: string; body: AssignRoleBody }) =>
      assignRoleRequest(input.userId, input.body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ADMIN_USERS_QUERY_KEY });
    },
  });
}

export function useRemoveRole() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: { userId: string; roleId: string }) =>
      removeRoleRequest(input.userId, input.roleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ADMIN_USERS_QUERY_KEY });
    },
  });
}

export function useAdminLogs(params: ListLogsParams) {
  return useQuery({
    queryKey: [...ADMIN_LOGS_QUERY_KEY_PREFIX, params],
    queryFn: () => listAdminLogsRequest(params),
  });
}
