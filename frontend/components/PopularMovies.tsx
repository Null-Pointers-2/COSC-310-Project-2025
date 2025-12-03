"use client";

import { useEffect, useState } from "react";
import { MovieCard } from "./movies/MovieCard";

interface PopularMovie {
  movie_id: number;
  score: number;
  vote_count: number;
  avg_rating: number;
  title: string;
  tmdb_id?: number;
}

export function PopularMovies() {
  const [movies, setMovies] = useState<PopularMovie[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPopular() {
      try {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${API_BASE_URL}/ranking/popular`);

        if (!res.ok) throw new Error("Failed to fetch");
        const data = await res.json();
        setMovies(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchPopular();
  }, []);

  if (loading) return (
    <div className="w-full h-64 bg-gray-100 animate-pulse rounded-xl mb-12"></div>
  );

  if (movies.length === 0) return null;

  return (
    <div className="space-y-4 py-4">
      <div className="flex items-center justify-between px-1">
        <h2 className="text-xl font-bold text-gray-900">Popular Now</h2>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 px-2">
        {movies.map((movie, index) => (
          <div key={movie.movie_id} className="relative group w-full">
              <MovieCard
                title={movie.title}
                movieId={movie.movie_id}
                tmdbId={movie.tmdb_id}
                subtitle={`Rating Score ${Math.round((movie.score / 5.0) * 100)}%`}
              />
            </div>
        ))}
      </div>
    </div>
  );
}
