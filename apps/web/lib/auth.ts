import { apiRequest } from "./api-client";

export interface CurrentUser {
  id: string;
  email: string;
  display_name: string;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

export interface RegisterInput {
  email: string;
  password: string;
  displayName: string;
}

export interface LoginInput {
  email: string;
  password: string;
}

function jsonRequest<T>(path: string, body: unknown): Promise<T | undefined> {
  return apiRequest<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function register(input: RegisterInput): Promise<CurrentUser | undefined> {
  return jsonRequest<CurrentUser>("/auth/register", {
    email: input.email,
    password: input.password,
    display_name: input.displayName,
  });
}

export function login(input: LoginInput): Promise<CurrentUser | undefined> {
  return jsonRequest<CurrentUser>("/auth/login", input);
}

export function getCurrentUser(): Promise<CurrentUser | undefined> {
  return apiRequest<CurrentUser>("/auth/me");
}
