"use client";

import { useState, useEffect } from "react";

export function useTMDB(title: string, tmdbId?: number | string) {
  const [posterUrl, setPosterUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPoster = async () => {
      if (!title && !tmdbId) {
        setLoading(false);
        return;
      }
      
      try {
        setLoading(true);
        const apiKey = process.env.NEXT_PUBLIC_TMDB_API_KEY;
        if (!apiKey) return;

        if (tmdbId) {
          const res = await fetch(
            `https://api.themoviedb.org/3/movie/${tmdbId}?api_key=${apiKey}`
          );
          if (res.ok) {
            const data = await res.json();
            if (data.poster_path) {
              setPosterUrl(`https://image.tmdb.org/t/p/w500${data.poster_path}`);
              return; 
            }
          }
        }

        // If ID not available try searching by move name (Secondary option needed for popularity ranking nowd)
        const cleanTitle = title.replace(/ \(\d{4}\)$/, '').trim();
        
        if (cleanTitle) {
            const searchRes = await fetch(
                `https://api.themoviedb.org/3/search/movie?api_key=${apiKey}&query=${encodeURIComponent(cleanTitle)}`
            );
            
            if (searchRes.ok) {
                const searchData = await searchRes.json();
                const bestMatch = searchData.results?.find((m: any) => m.poster_path);
                
                if (bestMatch) {
                    setPosterUrl(`https://image.tmdb.org/t/p/w500${bestMatch.poster_path}`);
                }
            }
        }

      } catch (err) {
        console.error("TMDB Image Error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchPoster();
  }, [title, tmdbId]);

  return { posterUrl, loading };
}