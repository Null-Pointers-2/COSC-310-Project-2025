import { api } from "./client";
import { User } from "../../types/user";

export interface UserUpdateData {
  username?: string;
  email?: string;
  password?: string;
}

export async function getMe() {
  return api("/users/me", { method: "GET" });
}

export async function updateMe(data: UserUpdateData) {
  return api("/users/me", { method: "PUT", body: data });
}
