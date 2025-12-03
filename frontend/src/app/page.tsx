"use client";

import Link from "next/link";
import { useAuth } from "@/../hooks/auth/useAuth";
import { useFetch } from "@/../hooks/useFetch";
import { RecommendationList } from "@/../components/recommendations/RecommendationList";
import { UserInsightsSummary } from "@/../types";
import { PopularMovies } from "@/../components/PopularMovies";

interface UserProfile {
  id: number;
  email: string;
  full_name?: string;
  username?: string;
}

export default function HomePage() {
  const { isAuthenticated, loading: authLoading } = useAuth();

  const { data: user, loading: userLoading } = useFetch<UserProfile>( // eslint-disable-line
    isAuthenticated ? "/users/me" : null
  );

  const { data: insights } = useFetch<UserInsightsSummary>(
    isAuthenticated ? "/insights/me/summary" : null
  );

  if (authLoading) {
    return (
      <div className="flex justify-center items-center h-[50vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">

      {isAuthenticated ? (
        <div className="space-y-12">

          <div className="flex flex-col items-center justify-center py-12 bg-white rounded-2xl shadow-sm border border-gray-100 text-center">
            <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight mb-3">
              Welcome back, {user?.username || user?.email || "Movie Fan"}
            </h1>

            {insights && insights.top_3_genres.length > 0 && (
              <div className="mt-4">
                <p className="text-sm text-gray-600 mb-3">Your favorite genres:</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {insights.top_3_genres.map((genre) => (
                    <Link
                      key={genre}
                      href={`/browse?genre=${encodeURIComponent(genre)}`}
                      className="px-4 py-2 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-colors text-sm font-medium"
                    >
                      {genre}
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>

          <section>
             <PopularMovies />
          </section>

          <section>
             <RecommendationList />
          </section>

        </div>

      ) : (
        <div className="text-center py-20">
          <h1 className="text-5xl font-bold text-gray-900 mb-6 tracking-tight">
            Track your <span className="text-indigo-600">favorite movies</span>
          </h1>
          <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
            {"Discover new films, rate what you've seen, and get personalized recommendations based on your unique taste."}
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link
              href="/register"
              className="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-all shadow-sm hover:shadow-md"
            >
              Get Started
            </Link>
            <Link
              href="/login"
              className="px-8 py-3 bg-white text-gray-700 font-semibold rounded-lg border border-gray-300 hover:bg-gray-50 transition-all"
            >
              Log in
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20 text-left">
            <div className="p-6 bg-white rounded-xl shadow-sm border border-gray-100">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 mb-4">
                ⭐
              </div>
              <h3 className="font-bold text-lg mb-2">Rate & Review</h3>
              <p className="text-gray-600">Share your thoughts on your favourite (and least favourite) films.</p>
            </div>
            <div className="p-6 bg-white rounded-xl shadow-sm border border-gray-100">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600 mb-4">
                🎯
              </div>
              <h3 className="font-bold text-lg mb-2">Personalized</h3>
              <p className="text-gray-600">{"Our system suggests movies you'll like based on your history."}</p>
            </div>
            <div className="p-6 bg-white rounded-xl shadow-sm border border-gray-100">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center text-green-600 mb-4">
                💾
              </div>
              <h3 className="font-bold text-lg mb-2">Export Data</h3>
              <p className="text-gray-600">Your data belongs to you. Export your ratings and lists anytime.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
