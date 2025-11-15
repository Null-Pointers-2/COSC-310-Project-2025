import { api } from "./client";
import { WatchlistItem } from "../../types/watchlist";

export async function getWatchlist() {
  return api("/watchlist", { method: "GET" });
}

export async function addToWatchlist(data: WatchlistItem) {
  return api("/watchlist", { method: "POST", body: data });
}

export async function removeFromWatchlist(id: string) {
  return api(`/watchlist/${id}`, { method: "DELETE" });
}
