"use client";

import { useState, useEffect } from "react";
import { useFetch } from "@/../hooks/useFetch";

export interface MovieDetails {
  movie_id: number;
  title: string;
  genres?: string[];
  tmdb_id?: number;
  average_rating?: number; 
  year?: number;           
  
  overview?: string;
  poster_path?: string; 
  backdrop_path?: string;
}

export function useMovie(movieId: string | number) {
  const { 
    data: localData, 
    loading: localLoading, 
    error: localError, 
    reload 
  } = useFetch<MovieDetails>(
    movieId ? `/movies/${movieId}` : null
  );

  const [tmdbData, setTmdbData] = useState<Partial<MovieDetails> | null>(null);
  const [tmdbLoading, setTmdbLoading] = useState(false);

  useEffect(() => {
    const fetchTMDBDetails = async () => {
      if (!localData) return;

      setTmdbLoading(true);
      try {
        const apiKey = process.env.NEXT_PUBLIC_TMDB_API_KEY;
        if (!apiKey) return;

        let data;
        if (localData.tmdb_id) {
            const res = await fetch(
                `https://api.themoviedb.org/3/movie/${localData.tmdb_id}?api_key=${apiKey}`
            );
            if (res.ok) {
                data = await res.json();
            }
        }

        if (data) {
          setTmdbData({
            overview: data.overview,
            poster_path: data.poster_path ? `https://image.tmdb.org/t/p/w500${data.poster_path}` : undefined,
            backdrop_path: data.backdrop_path ? `https://image.tmdb.org/t/p/original${data.backdrop_path}` : undefined,
          });
        }
      } catch (error) {
        console.error("Failed to fetch TMDB details:", error);
      } finally {
        setTmdbLoading(false);
      }
    };

    fetchTMDBDetails();
  }, [localData]); 

  const mergedMovie: MovieDetails | null = localData ? {
    ...localData,
    ...tmdbData
  } : null;

  return {
    movie: mergedMovie,
    loading: localLoading || tmdbLoading, 
    error: localError,
    reloadMovie: reload
  };
}