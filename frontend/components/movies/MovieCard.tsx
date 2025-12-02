"use client";

import Link from "next/link";
import { useTMDB } from "@/../hooks/tmdb/useTMDB";
import { WatchlistButton } from "@/../components/watchlist/WatchlistButton";

interface MovieCardProps {
  title: string;
  movieId?: string | number;
  tmdbId?: number;
  subtitle?: string;
  posterPath?: string;
}

export function MovieCard({ title, movieId, tmdbId, subtitle = "Movie", posterPath }: MovieCardProps) {
  const shouldFetch = !posterPath;
  
  const { posterUrl: fetchedUrl, loading: hookLoading } = useTMDB(
    shouldFetch ? title : "", 
    shouldFetch ? tmdbId : undefined
  );

  const displayPoster = posterPath || fetchedUrl;
  const isLoading = shouldFetch ? hookLoading : false;

  const Wrapper = movieId ? Link : "div";
  const wrapperProps = movieId ? { href: `/movies/${movieId}` } : {};

  return (
    // @ts-expect-error: this tag changes between a Link and a plain Div.
    <Wrapper 
      {...wrapperProps} 
      className="group block relative bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden border border-gray-200"
    >
      <div className="relative aspect-[2/3] w-full bg-gray-100 overflow-hidden">
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center text-gray-400">
            <svg className="animate-spin h-6 w-6" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>
        ) : displayPoster ? (
          <img // eslint-disable-line
            src={displayPoster}
            alt={title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center p-4 text-center bg-gray-100 text-gray-400">
            <span className="text-xs font-medium">No Poster</span>
          </div>
        )}
        
        {movieId && (
          <div className="absolute top-2 right-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <div onClick={(e) => e.stopPropagation()}>
               <WatchlistButton movieId={movieId} variant="icon" />
            </div>
          </div>
        )}
        
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-200 pointer-events-none" />
      </div>

      <div className="p-4">
        <h3 className="font-semibold text-gray-900 line-clamp-1 min-h-[1.5rem]" title={title}>
          {title || "Untitled"} 
        </h3>
        <p className="text-sm text-gray-500 mt-1 line-clamp-1">
           {subtitle}
        </p>
      </div>
    </Wrapper>
  );
}