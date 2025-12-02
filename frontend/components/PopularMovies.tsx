"use client";

import { useEffect, useState } from "react";
import { MovieCard } from "./movies/MovieCard";

interface PopularMovie {
  // Extra attributes needed for manual popularity lookup
  movie_id: number;
  score: number;
  vote_count: number;
  avg_rating: number;
  title: string;
}

export function PopularMovies() {
  const [movies, setMovies] = useState<PopularMovie[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPopular() {
      try {
        const res = await fetch("http://localhost:8000/ranking/popular");
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
    <div className="mb-16">
      <div className="text-center mb-10">
        <h2 className="text-xl font-bold text-gray-900 tracking-tight mb-3">
          Most Popular Now
        </h2>
      </div> 
   <div className="grid grid-cols-2 md:grid-cols-5 gap-4 px-2 pt-20"> 
        {movies.map((movie, index) => (
          <div key={movie.movie_id} className="relative group w-full">
            <div className="absolute -top-25 left-1/2 transform -translate-x-1/2 z-20 pointer-events-none w-full text-center">
              <span 
                className="text-7xl font-black text-indigo-600 tracking-tighter drop-shadow-md"
              >
                {index + 1}
              </span>
            </div>
             {/*Divide by conversion factor (5.0) to get a proper percentage value*/}
            <div className="h-full shadow-sm hover:shadow-md transition-shadow rounded-xl bg-white overflow-hidden w-full [&>*]:w-full">
                <MovieCard 
                title={movie.title}
                movieId={movie.movie_id}
                subtitle={`Rating Score ${Math.round((movie.score / 5.0) * 100)}%`}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}