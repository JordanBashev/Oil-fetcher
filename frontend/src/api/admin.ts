import { apiClient } from "./client";

export type AdminUser = {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
  roles: string[];
};

export type UserStatusBody = {
  is_active: boolean;
};

export type AssignRoleBody = {
  role_id: string;
};

export type Role = {
  id: string;
  name: string;
};

export type LogLine = {
  timestamp: string;
  level: string;
  logger: string;
  message: string;
};

export type LogFilters = {
  level?: string;
  logger?: string;
  search?: string;
  date_from?: string;
  date_to?: string;
};

export type ListLogsParams = LogFilters & {
  page: number;
  items_per_page: number;
};

export type PaginationMeta = {
  page: number;
  items_per_page: number;
  total_count: number;
  total_pages: number;
};

export type PaginatedLogs = {
  items: LogLine[];
  pagination: PaginationMeta;
};

export async function listAdminUsersRequest(): Promise<AdminUser[]> {
  const { data } = await apiClient.get<AdminUser[]>("/admin/users");
  return data;
}

export async function listAdminRolesRequest(): Promise<Role[]> {
  const { data } = await apiClient.get<Role[]>("/admin/roles");
  return data;
}

export async function deleteAdminUserRequest(userId: string): Promise<void> {
  await apiClient.delete(`/admin/users/${userId}`);
}

export async function setUserStatusRequest(userId: string, body: UserStatusBody): Promise<AdminUser> {
  const { data } = await apiClient.patch<AdminUser>(`/admin/users/${userId}/status`, body);
  return data;
}

export async function assignRoleRequest(userId: string, body: AssignRoleBody): Promise<AdminUser> {
  const { data } = await apiClient.post<AdminUser>(`/admin/users/${userId}/roles`, body);
  return data;
}

export async function removeRoleRequest(userId: string, roleId: string): Promise<AdminUser> {
  const { data } = await apiClient.delete<AdminUser>(`/admin/users/${userId}/roles/${roleId}`);
  return data;
}

export async function listAdminLogsRequest(params: ListLogsParams): Promise<PaginatedLogs> {
  const { data } = await apiClient.get<PaginatedLogs>("/admin/logs", { params });
  return data;
}
