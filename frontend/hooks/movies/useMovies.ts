"use client";

import { useState, useEffect } from "react";

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
  const [movies, setMovies] = useState<MovieSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    setMovies([]);
    setHasMore(true);
  }, [query, genre]);

  useEffect(() => {
    const fetchMovies = async () => {
      if (!hasMore && page > 1) return;

      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams();
        params.append("page", page.toString());
        params.append("page_size", "20");

        if (query) {
          params.append("query", query);
        }

        if (genre && genre !== "All") {
          params.append("genre", genre);
        }

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${apiUrl}/movies?${params.toString()}`);

        if (!response.ok) {
          throw new Error("Failed to fetch movies");
        }

        const data = await response.json();

        const newMovies = data.movies || [];

        if (newMovies.length < 20) {
            setHasMore(false);
        } else {
            if (data.total_pages && page >= data.total_pages) {
                setHasMore(false);
            } else {
                setHasMore(true);
            }
        }

        setMovies((prev) => {
            if (page === 1) return newMovies;

            const existingIds = new Set(prev.map(m => m.movie_id));
            const uniqueNew = newMovies.filter((m: MovieSummary) => !existingIds.has(m.movie_id));
            return [...prev, ...uniqueNew];
        });

      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoading(false);
      }
    };

    fetchMovies();
  }, [page, query, genre]);

  return {
    movies,
    loading,
    error,
    hasMore
  };
}
