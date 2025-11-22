import { api } from "./client";

export async function getRecommendations() {
  return api("/recommendations/me", { method: "GET" });
}

export async function refreshRecommendations() {
  return api("/recommendations/me/refresh", { method: "POST" });
}

export async function getSimilarRecommendations(id: string) {
  return api(`/recommendations/similar/${id}`, { method: "GET" });
}
