"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter, usePathname } from "next/navigation";

export function useAuth() {
  const [token, setToken] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    if (storedToken) {
      setToken(storedToken);
      setIsAuthenticated(true);
    } else {
      setToken(null);
      setIsAuthenticated(false);
    }
    setLoading(false);
  }, [pathname]);

  const login = useCallback((newToken: string) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
    setIsAuthenticated(true);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setToken(null);
    setIsAuthenticated(false);
    router.push("/login");
    router.refresh();
  }, [router]);

  const authFetch = useCallback(
    async (endpoint: string, options: RequestInit = {}) => {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      const currentToken = token || localStorage.getItem("token");

      const headers = {
        "Content-Type": "application/json",
        ...options.headers,
        Authorization: currentToken ? `Bearer ${currentToken}` : "",
      };

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
      });

      if (response.status === 401) {
        logout();
        throw new Error("Session expired");
      }

      return response;
    },
    [token, logout]
  );

  return { token, isAuthenticated, loading, login, logout, authFetch };
}
