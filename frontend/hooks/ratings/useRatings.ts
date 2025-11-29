"use client";

import { useState } from "react";
import { useFetch } from "@/../hooks/useFetch";
import { useAuth } from "@/../hooks/auth/useAuth";

export interface Rating {
  id: number;
  movie_id: number;
  user_id: number;
  rating: number; // 0.5 to 5.0
  created_at: string;
}

export function useRatings() {

  const { data: ratings, loading, error, reload } = useFetch<Rating[]>("/ratings/me");
  
  const { authFetch } = useAuth();
  const [submitting, setSubmitting] = useState(false);

  const getRatingForMovie = (movieId: number | string) => {
    if (!ratings) return null;
    return ratings.find((r) => r.movie_id === Number(movieId)) || null;
  };


  const createRating = async (movieId: number | string, score: number) => {
    setSubmitting(true);
    try {
      const res = await authFetch("/ratings", {
        method: "POST",
        body: JSON.stringify({ movie_id: movieId, rating: score }),
      });
      
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to create rating");
      }
      
      reload();
      return await res.json();
    } catch (err) {
      console.error(err);
      throw err;
    } finally {
      setSubmitting(false);
    }
  };

  const updateRating = async (ratingId: number, score: number) => {
    setSubmitting(true);
    try {
      const res = await authFetch(`/ratings/${ratingId}`, {
        method: "PUT",
        body: JSON.stringify({ rating: score }),
      });

      if (!res.ok) throw new Error("Failed to update rating");
      
      reload();
      return await res.json();
    } catch (err) {
      console.error(err);
      throw err;
    } finally {
      setSubmitting(false);
    }
  };

  const deleteRating = async (ratingId: number) => {
    setSubmitting(true);
    try {
      const res = await authFetch(`/ratings/${ratingId}`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error("Failed to delete rating");
      
      reload();
      return true;
    } catch (err) {
      console.error(err);
      throw err;
    } finally {
      setSubmitting(false);
    }
  };

  return {
    ratings: ratings || [],
    loading,
    error,
    submitting,
    getRatingForMovie,
    createRating,
    updateRating,
    deleteRating,
    reloadRatings: reload,
  };
}