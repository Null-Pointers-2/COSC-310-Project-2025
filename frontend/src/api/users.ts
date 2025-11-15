import { api } from "./client";
import { User } from "../../types/user";

export async function getMe() {
  return api("/users/me", { method: "GET" });
}

export async function updateMe(data: Partial<User>) {
  return api("/users/me", { method: "PUT", body: data });
}
