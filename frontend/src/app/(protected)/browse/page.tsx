"use client";

import { useState, useRef, useEffect } from "react";
import { useMovies } from "@/../hooks/movies/useMovies";
import { useRecommendations } from "@/../hooks/recommendations/useRecommendations";
import { MovieCard } from "@/../components/movies/MovieCard";
import { useAuth } from "@/../hooks/auth/useAuth";
import { useFetch } from "@/../hooks/useFetch";

export default function BrowsePage() {
  const [searchInput, setSearchInput] = useState("");
  const [activeQuery, setActiveQuery] = useState("");
  const [selectedGenre, setSelectedGenre] = useState("");
  const [page, setPage] = useState(1);

  const { isAuthenticated } = useAuth();

  const observerTarget = useRef(null);

  const { data: genresList } = useFetch<string[]>("/movies/genres");
  const genres = genresList || [];

  const { movies, loading: moviesLoading, hasMore } = useMovies({
    query: activeQuery,
    genre: selectedGenre,
    page: page
  });

  const { recommendations } = useRecommendations();
  const isFiltering = activeQuery.length > 0 || selectedGenre.length > 0;

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !moviesLoading) {
          setPage((prev) => prev + 1);
        }
      },
      { threshold: 0.1 }
    );

    const target = observerTarget.current;
    if (target) {
      observer.observe(target);
    }

    return () => {
      if (target) {
        observer.unobserve(target);
      }
      observer.disconnect();
    };
  }, [hasMore, moviesLoading]);

  const handleSearch = () => {
    setActiveQuery(searchInput);
    setPage(1);
  };

  const handleClear = () => {
    setSearchInput("");
    setActiveQuery("");
    setSelectedGenre("");
    setPage(1);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Browse Movies</h1>

        <div className="flex flex-col md:flex-row gap-4">

          <div className="flex-1 flex gap-2">
            <div className="relative flex-1">
              <input
                type="text"
                placeholder="Search by title..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all outline-none"
              />
              <svg className="w-5 h-5 text-gray-400 absolute left-3 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <button
              onClick={handleSearch}
              className="px-6 py-3 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700 transition-colors shadow-sm cursor-pointer"
            >
              Search
            </button>
          </div>
        </div>

        {genres.length > 0 && (
          <div className="flex flex-wrap gap-2">
            <button
               onClick={() => {
                   setSelectedGenre("");
                   setPage(1);
               }}
               className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors cursor-pointer ${
                 selectedGenre === ""
                   ? "bg-gray-800 text-white"
                   : "bg-gray-100 text-gray-600 hover:bg-gray-200"
               }`}
            >
              All
            </button>
            {genres.map((genre) => (
              <button
                key={genre}
                onClick={() => {
                    setSelectedGenre(selectedGenre === genre ? "" : genre);
                    setPage(1);
                }}
                className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors cursor-pointer ${
                  selectedGenre === genre
                    ? "bg-indigo-600 text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {genre}
              </button>
            ))}
          </div>
        )}
      </div>

      {!isFiltering && isAuthenticated && recommendations.length > 0 && (
        <div className="pt-4 border-b border-gray-100 pb-8">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">✨</span>
            <h2 className="text-xl font-bold text-gray-900">Picked for You</h2>
          </div>

          <div className="flex gap-4 overflow-x-auto pb-4 snap-x scrollbar-thin scrollbar-thumb-gray-200">
            {recommendations.map((item) => (
              <div key={item.movie_id} className="min-w-[160px] w-[160px] snap-start">
                <MovieCard
                  title={item.title}
                  movieId={item.movie_id}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      <div>
        <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-900">
            {isFiltering ? "Search Results" : "Explore Library"}
            </h2>
            {isFiltering && (
                <button
                onClick={handleClear}
                className="text-indigo-600 font-medium hover:underline text-sm cursor-pointer"
                >
                Clear all filters
                </button>
            )}
        </div>

        {movies.length > 0 ? (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {movies.map((movie) => (
                <MovieCard
                  key={movie.movie_id}
                  title={movie.title}
                  movieId={movie.movie_id}
                  tmdbId={movie.tmdb_id}
                />
              ))}
            </div>

            <div ref={observerTarget} className="h-20 flex justify-center items-center mt-8">
              {moviesLoading && (
                  <div className="flex items-center space-x-2 text-gray-500">
                      <div className="w-4 h-4 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin"></div>
                      <span>Loading more movies...</span>
                  </div>
              )}
              {!hasMore && movies.length > 0 && (
                  <p className="text-gray-400 text-sm">You&apos;ve reached the end of the list</p>
              )}
            </div>
          </>
        ) : (
          !moviesLoading && (
            <div className="text-center py-20 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
              <p className="text-gray-500 text-lg">No movies found matching your criteria.</p>
              <button
                onClick={handleClear}
                className="mt-4 text-indigo-600 font-medium hover:underline cursor-pointer"
              >
                Clear filters
              </button>
            </div>
          )
        )}
      </div>
    </div>
  );
}
