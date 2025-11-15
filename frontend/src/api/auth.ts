import { api } from "./client";

export async function login(data: { username: string; password: string }) {
  return api("/auth/login", { method: "POST", body: data });
}

export async function register(data: { username: string; password: string }) {
  return api("/auth/register", { method: "POST", body: data });
}

export async function logout() {
  return api("/auth/logout", { method: "POST" });
}
