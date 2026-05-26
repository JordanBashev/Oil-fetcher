import { apiClient } from "./client";

export type User = {
  id: number;
  email: string;
  created_at: string;
  roles: string[];
};

export type AuthSuccess = {
  user: User;
};

export type Profile = {
  first_name: string;
  last_name: string;
  bio: string;
};

export type ProfileUpdate = Partial<Profile>;

export type Credentials = {
  email: string;
  password: string;
};

export async function registerRequest(credentials: Credentials): Promise<AuthSuccess> {
  const { data } = await apiClient.post<AuthSuccess>("/auth/register", credentials);
  return data;
}

export async function loginRequest(credentials: Credentials): Promise<AuthSuccess> {
  const { data } = await apiClient.post<AuthSuccess>("/auth/login", credentials);
  return data;
}

export async function logoutRequest(): Promise<void> {
  await apiClient.post("/auth/logout");
}

export async function refreshRequest(): Promise<AuthSuccess> {
  const { data } = await apiClient.post<AuthSuccess>("/auth/refresh");
  return data;
}

export async function getProfileRequest(): Promise<Profile> {
  const { data } = await apiClient.get<Profile>("/profile");
  return data;
}

export async function updateProfileRequest(changes: ProfileUpdate): Promise<Profile> {
  const { data } = await apiClient.put<Profile>("/profile", changes);
  return data;
}
