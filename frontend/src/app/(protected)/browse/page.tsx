"use client";

import { useState } from "react";
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

  const { data: genresList } = useFetch<string[]>("/movies/genres");

  const genres = genresList || [];

  const { movies, loading: moviesLoading } = useMovies({ 
    query: activeQuery, 
    genre: selectedGenre,
    page: page 
  });

  // 3. Fetch Personal Recommendations
  const { recommendations } = useRecommendations();

  const isFiltering = activeQuery.length > 0 || selectedGenre.length > 0;

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
              className="px-6 py-3 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700 transition-colors shadow-sm"
            >
              Search
            </button>
          </div>

          <select 
            value={selectedGenre}
            onChange={(e) => {
              setSelectedGenre(e.target.value);
              setPage(1);
            }}
            className="px-4 py-3 rounded-xl border border-gray-200 bg-white focus:border-indigo-500 outline-none cursor-pointer min-w-[150px]"
          >
            <option value="">All Genres</option>
            {genres.map(g => <option key={g} value={g}>{g}</option>)}
          </select>
        </div>

        {genres.length > 0 && (
          <div className="flex flex-wrap gap-2">
            <button
               onClick={() => setSelectedGenre("")}
               className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
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
                onClick={() => setSelectedGenre(selectedGenre === genre ? "" : genre)}
                className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
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
        <h2 className="text-xl font-bold text-gray-900 mb-6">
          {isFiltering ? "Search Results" : "Explore Library"}
        </h2>

        {moviesLoading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
            {[...Array(10)].map((_, i) => (
              <div key={i} className="aspect-[2/3] bg-gray-100 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : movies.length > 0 ? (
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

            <div className="mt-12 flex justify-center gap-4">
              <button
                disabled={page === 1}
                onClick={() => setPage(p => Math.max(1, p - 1))}
                className="px-6 py-2 border border-gray-300 rounded-lg disabled:opacity-50 hover:bg-gray-50"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(p => p + 1)}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                Next Page
              </button>
            </div>
          </>
        ) : (
          <div className="text-center py-20 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
            <p className="text-gray-500 text-lg">No movies found matching your criteria.</p>
            <button 
              onClick={handleClear}
              className="mt-4 text-indigo-600 font-medium hover:underline"
            >
              Clear filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
}