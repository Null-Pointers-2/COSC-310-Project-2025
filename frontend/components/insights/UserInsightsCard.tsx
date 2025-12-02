"use client";

import { useFetch } from "@/../hooks/useFetch";
import { UserInsights } from "@/../types";
import Link from "next/link";

export function UserInsightsCard() {
  const { data: insights, loading, error } = useFetch<UserInsights>("/insights/me");

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Your Insights</h2>
        <div className="animate-pulse space-y-4">
          <div className="h-20 bg-gray-100 rounded"></div>
          <div className="h-20 bg-gray-100 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !insights) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Your Insights</h2>
        <p className="text-gray-500 text-sm">
          {insights?.total_ratings === 0
            ? "Rate some movies to see your personalized insights"
            : "Unable to load insights"}
        </p>
      </div>
    );
  }

  if (insights.total_ratings === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Your Insights</h2>
        <p className="text-gray-500 text-sm">Rate some movies to see your personalized insights</p>
        <Link
          href="/browse"
          className="mt-4 inline-block text-indigo-600 hover:text-indigo-700 font-medium text-sm"
        >
          Browse Movies
        </Link>
      </div>
    );
  }

  const topGenres = insights.genre_insights.slice(0, 5);
  const topThemes = insights.theme_insights.slice(0, 5);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Your Insights</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">{insights.total_ratings}</div>
            <div className="text-xs text-gray-500 uppercase tracking-wide">Total Ratings</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {insights.average_rating?.toFixed(1) || "N/A"}
            </div>
            <div className="text-xs text-gray-500 uppercase tracking-wide">Avg Rating</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {insights.watchlist_metrics.completion_rate.toFixed(0)}%
            </div>
            <div className="text-xs text-gray-500 uppercase tracking-wide">Watchlist Complete</div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="font-bold text-gray-900 mb-4">Favorite Genres</h3>
        <div className="space-y-3">
          {topGenres.map((genre, index) => (
            <div key={genre.genre}>
              <div className="flex items-center justify-between mb-1">
                <Link
                  href={`/browse?genre=${encodeURIComponent(genre.genre)}`}
                  className="font-medium text-gray-900 hover:text-indigo-600"
                >
                  {index + 1}. {genre.genre}
                </Link>
                <div className="text-sm text-gray-600">
                  {genre.average_rating.toFixed(1)} avg · {genre.total_rated} rated
                </div>
              </div>
              <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-indigo-600 rounded-full"
                  style={{ width: `${genre.preference_score}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {topThemes.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="font-bold text-gray-900 mb-4">Favorite Themes</h3>
          <div className="flex flex-wrap gap-2">
            {topThemes.map((theme) => (
              <div
                key={theme.tag_id}
                className="px-3 py-2 bg-purple-50 text-purple-700 rounded-lg text-sm"
              >
                <div className="font-medium">{theme.tag}</div>
                <div className="text-xs text-purple-600">
                  {theme.average_rating.toFixed(1)} avg · {theme.movies_count} movies
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="font-bold text-gray-900 mb-4">Watchlist Stats</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Total Items:</span>
            <span className="font-medium text-gray-900">
              {insights.watchlist_metrics.total_watchlist_items}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Rated:</span>
            <span className="font-medium text-gray-900">
              {insights.watchlist_metrics.items_rated}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Not Rated:</span>
            <span className="font-medium text-gray-900">
              {insights.watchlist_metrics.items_not_rated}
            </span>
          </div>
          {insights.watchlist_metrics.average_time_to_rate_hours !== null && (
            <div className="flex justify-between">
              <span className="text-gray-600">Avg Time to Rate:</span>
              <span className="font-medium text-gray-900">
                {(insights.watchlist_metrics.average_time_to_rate_hours / 24).toFixed(1)} days
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
