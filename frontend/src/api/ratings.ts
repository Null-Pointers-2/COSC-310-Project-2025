import { api } from "./client";
import { Rating } from "../../types/rating";

export async function getRatings() {
  return api("/ratings", { method: "GET" });
}

export async function addRating(data: Omit<Rating, "id">) {
  return api("/ratings", { method: "POST", body: data });
}

export async function deleteRating(id: string) {
  return api(`/ratings/${id}`, { method: "DELETE" });
}
