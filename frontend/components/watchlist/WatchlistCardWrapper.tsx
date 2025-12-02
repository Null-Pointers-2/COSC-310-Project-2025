"use client";

import { useMovie } from "@/../hooks/movies/useMovie";
import { MovieCard } from "@/../components/movies/MovieCard";

interface WrapperProps {
  movieId: number;
}

export function WatchlistCardWrapper({ movieId }: WrapperProps) {
  const { movie, loading } = useMovie(movieId);

  if (loading) {
    return <div className="aspect-[2/3] bg-gray-100 rounded-xl animate-pulse" />;
  }

  if (!movie) {
    return null; 
  }

  const primaryGenre = movie.genres?.[0] || "Watchlist";

  return (
    <MovieCard 
      title={movie.title} 
      movieId={movie.movie_id} 
      tmdbId={movie.tmdb_id} // Pass the correct TMDB ID here
      subtitle={primaryGenre}
    />
  );
}