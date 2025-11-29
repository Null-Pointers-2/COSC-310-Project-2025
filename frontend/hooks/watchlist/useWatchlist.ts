"use client";

import { useState, useCallback } from "react";
import { useAuth } from "@/../hooks/auth/useAuth";

export function useWatchlist(movieId?: string | number) {
  const [loading, setLoading] = useState(false);
  const { authFetch, isAuthenticated } = useAuth();
  
  const checkInWatchlist = useCallback(async () => {
    if (!movieId || !isAuthenticated) return false;
    try {
      const res = await authFetch(`/watchlist/check/${movieId}`);
      return await res.json();
    } catch (error) {
      console.error(error);
      return false;
    }
  }, [movieId, isAuthenticated, authFetch]);

  const addToWatchlist = async (id: string | number) => {
    setLoading(true);
    try {
      const res = await authFetch(`/watchlist`, {
        method: "POST",
        body: JSON.stringify({ movie_id: id }),
      });
      if (!res.ok) throw new Error("Failed to add");
      return true;
    } catch (error) {
      console.error(error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const removeFromWatchlist = async (id: string | number) => {
    setLoading(true);
    try {
      const res = await authFetch(`/watchlist/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to remove");
      return true;
    } catch (error) {
      console.error(error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  return {
    addToWatchlist,
    removeFromWatchlist,
    checkInWatchlist,
    loading
  };
}