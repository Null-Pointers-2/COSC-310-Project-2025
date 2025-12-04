"use client";

import { GenreLeaderboard } from "@/../components/insights/GenreLeaderboard";

export default function LeaderboardPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Genre Leaderboard</h1>
        <p className="text-gray-600 mt-2">
          See what genres are most popular across all users
        </p>
      </div>

      <GenreLeaderboard />
    </div>
  );
}
