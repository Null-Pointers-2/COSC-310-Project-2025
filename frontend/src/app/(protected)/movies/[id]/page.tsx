"use client";

import { useParams } from "next/navigation";
import { useMovie } from "@/../hooks/movies/useMovie";
import { useSimilarMovies } from "@/../hooks/recommendations/useRecommendations";
import { WatchlistButton } from "@/../components/watchlist/WatchlistButton";
import { RatingForm } from "@/../components/ratings/RatingForm";
import { RecommendationCardWrapper } from "@/../components/recommendations/RecommendationCardWrapper";
import Link from "next/link";

export default function MovieDetailsPage() {
  const params = useParams();
  const movieId = params.id as string;

  const { movie, loading: movieLoading } = useMovie(movieId);
  const { similarMovies, loading: similarLoading } = useSimilarMovies(movieId);

  if (movieLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!movie) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-center p-4">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Movie not found</h1>
        <Link href="/browse" className="text-indigo-600 hover:underline">
          Back to Browse
        </Link>
      </div>
    );
  }

  const displayYear = movie.year || "N/A";
  const displayRating = movie.average_rating
    ? `${movie.average_rating.toFixed(1)} / 5`
    : "Not Rated";

  return (
    <div className="min-h-screen bg-white">
      <div className="relative h-[40vh] md:h-[50vh] w-full bg-gray-900 overflow-hidden">
        {movie.backdrop_path ? (
          <>
            <img // eslint-disable-line
              src={movie.backdrop_path}
              alt={movie.title}
              className="w-full h-full object-cover opacity-60"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-white via-transparent to-transparent" />
          </>
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200" />
        )}
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative -mt-32 md:-mt-48 pb-12">
        <div className="flex flex-col md:flex-row gap-8">

          <div className="flex-shrink-0 mx-auto md:mx-0">
            <div className="w-64 md:w-80 rounded-xl shadow-2xl overflow-hidden bg-white border-4 border-white">
              {movie.poster_path ? (
                <img // eslint-disable-line
                  src={movie.poster_path}
                  alt={movie.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="h-96 flex items-center justify-center bg-gray-200 text-gray-400">
                  No Poster
                </div>
              )}
            </div>

            <div className="mt-6 md:hidden space-y-4">
               <WatchlistButton movieId={movie.movie_id} variant="full" />
               <div className="bg-gray-50 p-4 rounded-xl border border-gray-100">
                 <RatingForm movieId={movie.movie_id} />
               </div>
            </div>
          </div>

          {/* Details */}
          <div className="flex-1 pt-4 md:pt-16">
            <div className="mb-2 flex flex-wrap items-center gap-3 text-sm font-medium">

               <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full">
                 {displayYear}
               </span>

               <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full flex items-center gap-1">
                 <span>★</span> {displayRating}
               </span>

               {movie.genres?.map(g => (
                 <span key={g} className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full">
                   {g}
                 </span>
               ))}
            </div>

            <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 mb-6 leading-tight">
              {movie.title}
            </h1>

            <div className="prose max-w-none text-gray-600 text-lg leading-relaxed mb-8 mt-12">
              <h3 className="text-gray-900 font-semibold mb-2">Overview</h3>
              <p>
                {movie.overview || "No description available."}
              </p>
            </div>

            <div className="hidden md:flex items-start gap-8 border-t border-gray-100 pt-8">
              <div>
                <h3 className="text-sm font-semibold text-gray-500 mb-3 uppercase tracking-wider">
                  Your Actions
                </h3>
                <WatchlistButton movieId={movie.movie_id} variant="full" />
              </div>

              <div className="flex-1 max-w-sm">
                 <h3 className="text-sm font-semibold text-gray-500 mb-3 uppercase tracking-wider">
                  Rate this Movie
                </h3>
                <RatingForm movieId={movie.movie_id} />
              </div>
            </div>
          </div>
        </div>

        <div className="mt-20">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">You Might Also Like</h2>

          {similarLoading ? (
             <div className="flex gap-4 overflow-hidden">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="min-w-[160px] h-[240px] bg-gray-100 rounded-xl animate-pulse"></div>
              ))}
            </div>
          ) : similarMovies.length > 0 ? (
            <div className="flex gap-4 overflow-x-auto pb-8 snap-x scrollbar-thin scrollbar-thumb-gray-200">
              {similarMovies.map((item) => (
                 <RecommendationCardWrapper
                    key={item.movie_id}
                    movieId={item.movie_id}
                    score={item.score || 0}
                 />
              ))}
            </div>
          ) : (
            <p className="text-gray-500 italic">No similar movies found.</p>
          )}
        </div>
      </div>
    </div>
  );
}
