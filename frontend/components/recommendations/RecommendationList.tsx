"use client";

import { useState } from "react";
import { useFetch } from "@/../hooks/useFetch";
import { useAuth } from "@/../hooks/auth/useAuth";
import { RecommendationCardWrapper } from "@/../components/recommendations/RecommendationCardWrapper";

interface RecommendationItem {
  movie_id: number;
  similarity_score: number;
}

interface RecommendationResponse {
  user_id: string;
  recommendations: RecommendationItem[];
}

export function RecommendationList() {
  const [refreshing, setRefreshing] = useState(false);
  
  const { data, loading, reload } = useFetch<RecommendationResponse>("/recommendations/me");
  const { authFetch } = useAuth();

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await authFetch("/recommendations/me/refresh", { method: "POST" });
      reload();
    } catch (error) {
      console.error("Refresh failed", error);
    } finally {
      setRefreshing(false);
    }
  };

  const recommendations = data?.recommendations || [];

  if (loading && !data) {
    return (
      <div className="py-8">
        <div className="h-6 w-48 bg-gray-200 rounded animate-pulse mb-4"></div>
        <div className="flex gap-4 overflow-hidden">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="min-w-[160px] h-[240px] bg-gray-100 rounded-xl animate-pulse"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!loading && recommendations.length === 0) {
    return (
      <div className="py-8 text-center bg-gray-50 rounded-xl border border-dashed border-gray-300">
        <h3 className="text-lg font-medium text-gray-900 mb-1">No recommendations yet</h3>
        <p className="text-gray-500 mb-4">
          Rate some movies to get personalized picks!
        </p>
        <button 
          onClick={handleRefresh}
          disabled={refreshing}
          className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
        >
          {refreshing ? "Generating..." : "Generate Now"}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4 py-4">
      <div className="flex items-center justify-between px-1">
        <h2 className="text-xl font-bold text-gray-900">Recommended for You</h2>
        
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className={`
            text-sm flex items-center gap-1 transition-colors
            ${refreshing ? "text-gray-400" : "text-indigo-600 hover:text-indigo-800"}
          `}
        >
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            fill="none" 
            viewBox="0 0 24 24" 
            strokeWidth={1.5} 
            stroke="currentColor" 
            className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
          </svg>
          {refreshing ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <div className="
        flex gap-4 overflow-x-auto pb-4 px-1
        scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent
        snap-x snap-mandatory
      ">
        {recommendations.map((item) => (
          <RecommendationCardWrapper 
            key={item.movie_id} 
            movieId={item.movie_id}
            score={item.similarity_score}
          />
        ))}
      </div>
    </div>
  );
}