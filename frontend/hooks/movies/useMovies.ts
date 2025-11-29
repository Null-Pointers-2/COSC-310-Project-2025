"use client";

import { useFetch } from "@/../hooks/useFetch";

export interface MovieSummary {
  movie_id: number;
  title: string;
  genres?: string[];
  average_rating?: number;
  tmdb_id?: number; 
}

interface UseMoviesOptions {
  query?: string;
  genre?: string;
  page?: number;
}

export function useMovies({ query, genre, page = 1 }: UseMoviesOptions = {}) {
  let endpoint = "/movies";

  const params = new URLSearchParams();
  if (page > 1) params.append("page", page.toString());
  
  if (query) {
    endpoint = "/movies/search";
    params.append("query", query);
  } else if (genre) {
    endpoint = "/movies/filter";
    params.append("genre", genre);
  }

  const queryString = params.toString();
  const finalUrl = queryString ? `${endpoint}?${queryString}` : endpoint;

  const { data, loading, error, reload } = useFetch<MovieSummary[]>(finalUrl);

  return {
    movies: data || [],
    loading,
    error,
    refreshMovies: reload
  };
}
