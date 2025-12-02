"use client";

import { useFetch } from "@/../hooks/useFetch";
import { useAuth } from "@/../hooks/auth/useAuth";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useEffect, useState } from "react";

interface Rating {
  id: number;
  movie_id: number;
  user_id: string;
  rating: number;
  timestamp: string;
}

interface Movie {
  movie_id: number;
  title: string;
  genres: string[];
}

export default function RatingsPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();

  if (!authLoading && !isAuthenticated) {
    router.push("/login");
  }

  const {
    data: ratings,
    loading: ratingsLoading,
    error: ratingsError
  } = useFetch<Rating[]>("/ratings/me");

  const [movies, setMovies] = useState<Record<number, Movie>>({});
  const [moviesLoading, setMoviesLoading] = useState(false);

  useEffect(() => {
    const fetchMovies = async () => {
      if (!ratings || ratings.length === 0) return;

      setMoviesLoading(true);
      const movieData: Record<number, Movie> = {};

      const uniqueMovieIds = Array.from(new Set(ratings.map(r => r.movie_id)));

      try {
          const promises = uniqueMovieIds.map(id =>
              fetch(`${process.env.NEXT_PUBLIC_API_URL}/movies/${id}`)
                  .then(res => {
                    if (!res.ok) throw new Error(`Failed to fetch movie ${id}`);
                    return res.json();
                  })
                  .then(data => { movieData[id] = data; })
                  .catch(err => console.error(`Failed to load movie ${id}`, err))
          );

          await Promise.all(promises);
          setMovies(movieData);
      } catch (error) {
          console.error("Error fetching movies", error);
      } finally {
          setMoviesLoading(false);
      }
    };

    if (ratings) {
        fetchMovies();
    }
  }, [ratings]);


  if (authLoading || ratingsLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (ratingsError) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-4">
        <div className="bg-white p-8 rounded-xl shadow-sm border border-red-100 text-center max-w-md w-full">
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-6 h-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-lg font-bold text-gray-900 mb-2">Error Loading Ratings</h2>
          <p className="text-gray-500 mb-6">{ratingsError}</p>
          <button
            onClick={() => window.location.reload()}
            className="w-full py-2 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Your Ratings</h1>
            <p className="text-gray-500 mt-1">
              You have rated {ratings?.length || 0} movies
            </p>
          </div>
          <Link
            href="/browse"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
          >
            Rate More Movies
          </Link>
        </div>

        {!ratings || ratings.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <div className="w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900">No ratings yet</h3>
            <p className="mt-2 text-gray-500 max-w-sm mx-auto">
              Start rating movies to get personalized recommendations and track what you&apos;ve watched.
            </p>
            <div className="mt-6">
              <Link href="/browse" className="text-indigo-600 hover:text-indigo-500 font-medium">
                Browse movies &rarr;
              </Link>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <ul className="divide-y divide-gray-100">
              {ratings.map((rating) => {
                const movie = movies[rating.movie_id];
                return (
                  <li key={rating.id} className="group hover:bg-gray-50 transition-colors">
                    <div className="px-6 py-4 flex items-center justify-between">
                      <div className="flex items-center min-w-0 gap-4">
                        <div className="flex-shrink-0 w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center text-lg font-bold text-gray-400">
                          {movie ? movie.title[0] : "?"}
                        </div>
                        <div className="min-w-0">
                          <Link href={`/movies/${rating.movie_id}`} className="text-sm font-medium text-gray-900 hover:text-indigo-600 truncate block">
                            {movie ? movie.title : `Movie #${rating.movie_id}`}
                          </Link>
                          <p className="text-xs text-gray-500 truncate">
                            {movie ? movie.genres.join(", ") : moviesLoading ? "Loading..." : "Unknown Genre"}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            Rated on {new Date(rating.timestamp).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="flex items-center bg-yellow-50 px-3 py-1 rounded-full border border-yellow-100">
                          <svg className="w-4 h-4 text-yellow-400 mr-1.5" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                          <span className="font-bold text-yellow-700">{rating.rating}</span>
                        </div>
                        <Link
                          href={`/movies/${rating.movie_id}`}
                          className="text-gray-400 hover:text-indigo-600 transition-colors p-2 rounded-full hover:bg-indigo-50"
                        >
                          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </Link>
                      </div>
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
