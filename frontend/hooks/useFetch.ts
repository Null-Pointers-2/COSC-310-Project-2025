"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/../hooks/auth/useAuth";

interface FetchState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useFetch<T>(endpoint: string | null) {
  const [state, setState] = useState<FetchState<T>>({
    data: null,
    loading: !!endpoint,
    error: null,
  });
  
  const { token, loading: authLoading } = useAuth();

  const fetchData = useCallback(async () => {
    if (!endpoint) return;

    if (authLoading) return;

    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, { headers });

      if (response.status === 401) {
        throw new Error("Unauthorized");
      }

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({ 
        data: null, 
        loading: false, 
        error: err instanceof Error ? err.message : "An unknown error occurred" 
      });
    }
  }, [endpoint, token, authLoading]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { ...state, reload: fetchData };
}