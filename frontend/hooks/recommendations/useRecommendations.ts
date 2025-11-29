"use client";

import { useState } from "react";
import { useFetch } from "@/../hooks/useFetch";
import { useAuth } from "@/../hooks/auth/useAuth";

export interface RecommendationItem {
  movie_id: number;
  title: string;
  score?: number;
}

interface RecommendationResponse {
  items: RecommendationItem[];
  generated_at?: string;
}

export function useRecommendations() {
  const { authFetch } = useAuth();
  const [refreshing, setRefreshing] = useState(false);

  const { 
    data, 
    loading, 
    error, 
    reload 
  } = useFetch<RecommendationResponse>("/recommendations/me");

  const refreshRecommendations = async () => {
    setRefreshing(true);
    try {
      const res = await authFetch("/recommendations/me/refresh", {
        method: "POST",
      });
      
      if (!res.ok) throw new Error("Failed to refresh recommendations");
      
      reload();
    } catch (err) {
      console.error(err);
    } finally {
      setRefreshing(false);
    }
  };

  return {
    recommendations: data?.items || [],
    loading,
    error,
    refreshing,
    refreshRecommendations,
  };
}

export function useSimilarMovies(movieId?: number | string) {
  const endpoint = movieId ? `/recommendations/similar/${movieId}` : null;
  
  const { data, loading, error } = useFetch<RecommendationItem[]>(endpoint);

  return {
    similarMovies: data || [],
    loading,
    error,
  };
}