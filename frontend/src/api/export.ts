import { api } from "./client";

export async function exportProfile() {
  return api("/export/profile", { method: "GET" });
}

export async function exportRatings() {
  return api("/export/ratings", { method: "GET" });
}

export async function exportRecommendations() {
  return api("/export/recommendations", { method: "GET" });
}

export async function exportAll() {
  return api("/export/all", { method: "GET" });
}
