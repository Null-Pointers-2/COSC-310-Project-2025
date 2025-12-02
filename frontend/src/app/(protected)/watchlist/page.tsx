"use client";

import { useRouter } from "next/navigation";
import { useFetch } from "@/../hooks/useFetch";
import { useAuth } from "@/../hooks/auth/useAuth";
import { WatchlistCardWrapper } from "@/../components/watchlist/WatchlistCardWrapper";
import Link from "next/link";

interface WatchlistItem {
  movie_id: number;
}

export default function WatchlistPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();

  if (!authLoading && !isAuthenticated) {
    router.push("/login");
  }

  const { data: watchlist, loading: listLoading, error } = useFetch<WatchlistItem[]>("/watchlist");

  if (authLoading || listLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">My Watchlist</h1>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="aspect-[2/3] bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-20 text-red-600">
        Error loading watchlist: {error}
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 min-h-screen">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">My Watchlist</h1>
        <p className="text-gray-500 mt-1">
          {watchlist?.length || 0} movies saved to watch later
        </p>
      </div>

      {watchlist && watchlist.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
          {watchlist.map((item) => (
            <WatchlistCardWrapper 
              key={item.movie_id} 
              movieId={item.movie_id} 
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-32">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4 text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-8 h-8">
              <path strokeLinecap="round" strokeLinejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0111.186 0z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900">Your watchlist is empty</h2>
          <p className="text-gray-500 mt-2 mb-8 max-w-sm mx-auto">
            Movies you want to watch will appear here. Go explore and find something great!
          </p>
          <Link 
            href="/browse"
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
          >
            Browse Movies
          </Link>
        </div>
      )}
    </div>
  );
}