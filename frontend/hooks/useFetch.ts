"use client";

export function useFetch<T>(_fetcher: () => Promise<T>) {
  return { data: null as T | null, loading: false };
}
