import { api } from "./client";

export async function getMovies() {
  return api("/movies", { method: "GET" });
}

export async function getMovie(id: string) {
  return api(`/movies/${id}`, { method: "GET" });
}
