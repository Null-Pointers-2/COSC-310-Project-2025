import { api } from "./client";

export async function getAdminDashboard() {
  return api("/admin", { method: "GET" });
}
