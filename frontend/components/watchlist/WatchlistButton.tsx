"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface WatchlistButtonProps {
  movieId: number | string;
  onToggle?: (isInWatchlist: boolean) => void;
  variant?: "icon" | "full";
}

export function WatchlistButton({ movieId, onToggle, variant = "full" }: WatchlistButtonProps) {
  const [isInWatchlist, setIsInWatchlist] = useState(false);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          setLoading(false);
          return;
        }

        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${API_BASE_URL}/watchlist/check/${movieId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.ok) {
          const data = await response.json();
          setIsInWatchlist(data);
        }
      } catch (error) {
        console.error("Failed to check watchlist status", error);
      } finally {
        setLoading(false);
      }
    };

    checkStatus();
  }, [movieId]);

  const toggleWatchlist = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/auth/login");
      return;
    }


    const previousState = isInWatchlist;
    setIsInWatchlist(!previousState);

    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      let response;

      if (previousState) {
        response = await fetch(`${API_BASE_URL}/watchlist/${movieId}`, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token}` },
        });
      } else {
        response = await fetch(`${API_BASE_URL}/watchlist`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ movie_id: movieId }),
        });
      }

      if (!response.ok) {
        throw new Error("Failed to update watchlist");
      }

      if (onToggle) onToggle(!previousState);
      router.refresh();

    } catch (error) {
      console.error(error);
      setIsInWatchlist(previousState);
      alert("Something went wrong. Please try again.");
    }
  };

  if (loading) {
    return (
      <div className={`animate-pulse bg-gray-200 rounded ${variant === 'icon' ? 'w-8 h-8' : 'w-[200px] h-10'}`} />
    );
  }

  if (variant === "icon") {
    return (
      <button
        onClick={toggleWatchlist}
        className={`p-2 rounded-full backdrop-blur-sm transition-all duration-200 cursor-pointer hover:scale-110 active:scale-95
          ${isInWatchlist
            ? "bg-rose-500/10 text-rose-600 hover:bg-rose-500/20"
            : "bg-black/20 text-white hover:bg-rose-500 hover:text-white"
          }`}
        title={isInWatchlist ? "Remove from Watchlist" : "Add to Watchlist"}
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill={isInWatchlist ? "currentColor" : "none"} viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
        </svg>
      </button>
    );
  }

  return (
    <button
      onClick={toggleWatchlist}
      className={`
        flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 cursor-pointer w-[200px] whitespace-nowrap
        ${isInWatchlist
          ? "bg-rose-50 text-rose-600 border border-rose-200 hover:bg-white"
          : "bg-gray-900 text-white hover:bg-gray-700"
        }
      `}
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill={isInWatchlist ? "currentColor" : "none"} viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5 shrink-0">
        <path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
      </svg>
      {isInWatchlist ? "In Watchlist" : "Add to Watchlist"}
    </button>
  );
}
