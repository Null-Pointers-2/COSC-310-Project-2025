"use client";

import { useFetch } from "@/../hooks/useFetch";
import { GlobalGenreLeaderboard } from "@/../types";
import Link from "next/link";

export function GenreLeaderboard() {
  const { data: leaderboard, loading, error } = useFetch<GlobalGenreLeaderboard>(
    "/global-insights/genre-leaderboard"
  );

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Most Popular Genres</h2>
        <div className="animate-pulse space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-10 bg-gray-100 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !leaderboard) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Most Popular Genres</h2>
        <p className="text-gray-500 text-sm">Unable to load genre statistics</p>
      </div>
    );
  }

  const topGenres = leaderboard.genres.slice(0, 10);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="mb-4">
        <h2 className="text-lg font-bold text-gray-900">Most Popular Genres</h2>
        <p className="text-xs text-gray-500 mt-1">
          {leaderboard.total_ratings.toLocaleString()} ratings from {leaderboard.total_users} users
        </p>
      </div>

      <div className="space-y-2">
        {topGenres.map((genreStats, index) => {
          const rank = index + 1;

          return (
            <Link
              key={genreStats.genre}
              href={`/browse?genre=${encodeURIComponent(genreStats.genre)}`}
              className="flex items-center gap-3 p-2 rounded hover:bg-gray-50 transition-colors"
            >
              <div className="flex-shrink-0 w-6 text-sm font-medium text-gray-500">
                {rank}
              </div>

              <div className="flex-1">
                <div className="font-medium text-gray-900">{genreStats.genre}</div>
                <div className="text-xs text-gray-500">
                  {genreStats.total_ratings.toLocaleString()} ratings · {genreStats.average_rating.toFixed(1)} avg
                </div>
              </div>

              <div className="text-sm text-gray-600">
                {Math.round(genreStats.popularity_score)}
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
