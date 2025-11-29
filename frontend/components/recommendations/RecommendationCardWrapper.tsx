"use client";

import { useMovie } from "@/../hooks/movies/useMovie";
import { MovieCard } from "@/../components/movies/MovieCard";

interface WrapperProps {
  movieId: number;
  score: number;
}

export function RecommendationCardWrapper({ movieId, score }: WrapperProps) {
  const { movie, loading } = useMovie(movieId);

  if (loading) {
    return <div className="min-w-[160px] h-[240px] bg-gray-100 rounded-xl animate-pulse" />;
  }

  if (!movie) {
    return null;
  }

  const matchPercentage = Math.round(score * 100);

  return (
    <div className="min-w-[160px] w-[160px] snap-start relative">
      <MovieCard 
        title={movie.title} 
        movieId={movie.movie_id}
        tmdbId={movie.tmdb_id}
        posterPath={movie.poster_path}
        subtitle={`${matchPercentage}% Match`}
      />
    </div>
  );
}