"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/../hooks/auth/useAuth";
import { useFetch } from "@/../hooks/useFetch";
import { MovieCard } from "@/../components/movies/MovieCard";
import Link from "next/link";

interface RecommendationItem {
  movie_id: number;
  similarity_score: number;
}

type RecommendationsResponse = RecommendationItem[] | { recommendations: RecommendationItem[] };

interface GameMovie {
  movie_id: number;
  title: string;
  poster_path?: string;
  tmdb_id?: number;
  average_rating: number; 
  match_score: number;    
}

type GameState = "loading" | "rating_guess" | "rating_reveal" | "match_guess" | "match_reveal" | "game_over" | "error";

export default function GamePage() {
  const { authFetch, isAuthenticated, loading: authLoading } = useAuth();
  
  const [gameState, setGameState] = useState<GameState>("loading");
  const [movieA, setMovieA] = useState<GameMovie | null>(null);
  const [movieB, setMovieB] = useState<GameMovie | null>(null);
  const [score, setScore] = useState(0);
  const [round, setRound] = useState(1);
  const [matchGuess, setMatchGuess] = useState<number>(50); 

  useFetch<unknown>("recommendations/me/refresh?limit=50")

  const { 
    data: recData, 
    loading: recLoading, 
    error: recError 
  } = useFetch<RecommendationsResponse>("/recommendations/me?limit=50");

  const loadRound = useCallback(async (attempts = 0) => {
    if (!recData) return;
    
    if (attempts > 3) {
      setGameState("error");
      return;
    }
    
    const list: RecommendationItem[] = Array.isArray(recData) ? recData : recData.recommendations || [];

    if (list.length < 2) {
      setGameState("game_over");
      return;
    }

    if (attempts === 0) setGameState("loading");

    const idx1 = Math.floor(Math.random() * list.length);
    let idx2 = Math.floor(Math.random() * list.length);
    while (idx1 === idx2) idx2 = Math.floor(Math.random() * list.length);

    const itemA = list[idx1];
    const itemB = list[idx2];

    try {
      const [resA, resB] = await Promise.all([
        authFetch(`/movies/${itemA.movie_id}`),
        authFetch(`/movies/${itemB.movie_id}`)
      ]);

      if (!resA.ok || !resB.ok) throw new Error("Failed to fetch movie details");

      const detailsA = await resA.json();
      const detailsB = await resB.json();

      const ratingA = (typeof detailsA.average_rating === 'number') ? detailsA.average_rating : 0;
      const ratingB = (typeof detailsB.average_rating === 'number') ? detailsB.average_rating : 0;

      setMovieA({ ...detailsA, average_rating: ratingA, match_score: itemA.similarity_score });
      setMovieB({ ...detailsB, average_rating: ratingB, match_score: itemB.similarity_score });

      setGameState("rating_guess");
      setMatchGuess(50);
    } catch (err) {
      console.error("Round setup failed:", err);
      loadRound(attempts + 1);
    }
  }, [recData, authFetch]);

  useEffect(() => {
    if (recData && !movieA) {
      loadRound();
    } else if (recError) {
      setGameState("error");
    }
  }, [recData, recError, loadRound, movieA]);

  const handleRatingGuess = (selectedId: number) => {
    if (!movieA || !movieB) return;
    
    const selectedMovie = selectedId === movieA.movie_id ? movieA : movieB;
    const otherMovie = selectedId === movieA.movie_id ? movieB : movieA;
    if (selectedMovie.average_rating >= otherMovie.average_rating) {
      setScore(s => s + 1);
    }
    
    setGameState("rating_reveal");
  };

  const handleMatchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setGameState("match_reveal");
  };

  const nextRound = () => {
    setRound(r => r + 1);
    setMovieA(null); 
    setMovieB(null);
    setGameState("loading");
  };


  if (authLoading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4">
        <h1 className="text-3xl font-bold mb-4">Best Movie?</h1>
        <p className="mb-6">Log in to play against your own personalized recommendations!</p>
        <Link href="/login" className="bg-indigo-600 text-white px-6 py-2 rounded-lg">Log In</Link>
      </div>
    );
  }

  if (gameState === "error" || recError) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4 text-center">
        <h2 className="text-xl font-bold text-red-600 mb-2">Error Loading Game</h2>
        <button onClick={() => window.location.reload()} className="text-indigo-600 underline">Try Again</button>
      </div>
    );
  }

  if (recLoading || gameState === "loading" || !movieA || !movieB) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        <p className="text-gray-500 animate-pulse">Finding a matchup...</p>
      </div>
    );
  }

  if (gameState === "game_over") {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4 text-center">
        <h1 className="text-4xl font-bold mb-2">Game Over</h1>
        <p className="text-gray-600 mb-6">We ran out of data!</p>
        <Link href="/browse" className="text-indigo-600 underline">Browse Movies</Link>
      </div>
    );
  }

  const winningMovie = movieA.average_rating >= movieB.average_rating ? movieA : movieB;

  return (
    <div className="min-h-screen bg-white flex flex-col">
      
      <div className="w-full border-b border-gray-100 bg-white/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-3 flex justify-between items-center">
          <h1 className="text-xl font-bold text-indigo-900 tracking-tight">Best Movie?</h1>
          <div className="bg-indigo-50 px-3 py-1 rounded-full font-mono text-sm text-indigo-700 font-bold">
            Score: {score} | Round: {round}
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col justify-center py-8 px-4">
        <div className="max-w-5xl mx-auto w-full">
          
          {(gameState === "rating_guess" || gameState === "rating_reveal") && (
            <div className="space-y-6 text-center">
              <h2 className="text-2xl md:text-3xl font-extrabold text-gray-900">
                Which has a <span className="text-indigo-600">Higher Rating?</span>
              </h2>
              
              <div className="flex flex-col md:flex-row gap-4 md:gap-12 items-center justify-center relative">
                
                <div 
                  onClick={() => gameState === "rating_guess" && handleRatingGuess(movieA.movie_id)}
                  className={`w-48 md:w-64 relative cursor-pointer transition-all duration-300 hover:scale-105 ${gameState === "rating_guess" ? "hover:ring-4 ring-indigo-200 rounded-xl" : ""}`}
                >
                  <div className="pointer-events-none">
                    <MovieCard 
                      title={movieA.title} 
                      movieId={movieA.movie_id} 
                      tmdbId={movieA.tmdb_id}
                      subtitle={gameState === "rating_reveal" ? `Rating: ${movieA.average_rating.toFixed(1)}` : "???"} 
                    />
                  </div>
                  {gameState === "rating_reveal" && (
                    <div className={`mt-2 text-xl font-bold ${movieA.average_rating >= movieB.average_rating ? "text-green-600" : "text-red-500"}`}>
                      {movieA.average_rating.toFixed(1)}
                    </div>
                  )}
                </div>

                <div className="z-10 bg-white p-3 rounded-full shadow-lg font-black text-lg text-gray-300 border-2 border-gray-100">
                  VS
                </div>

                <div 
                  onClick={() => gameState === "rating_guess" && handleRatingGuess(movieB.movie_id)}
                  className={`w-48 md:w-64 relative cursor-pointer transition-all duration-300 hover:scale-105 ${gameState === "rating_guess" ? "hover:ring-4 ring-indigo-200 rounded-xl" : ""}`}
                >
                  <div className="pointer-events-none">
                    <MovieCard 
                      title={movieB.title} 
                      movieId={movieB.movie_id} 
                      tmdbId={movieB.tmdb_id}
                      subtitle={gameState === "rating_reveal" ? `Rating: ${movieB.average_rating.toFixed(1)}` : "???"} 
                    />
                  </div>
                  {gameState === "rating_reveal" && (
                    <div className={`mt-2 text-xl font-bold ${movieB.average_rating >= movieA.average_rating ? "text-green-600" : "text-red-500"}`}>
                      {movieB.average_rating.toFixed(1)}
                    </div>
                  )}
                </div>
              </div>

              {gameState === "rating_reveal" && (
                <div className="mt-6 animate-bounce">
                  <button 
                    onClick={() => setGameState("match_guess")}
                    className="bg-gray-900 text-white px-8 py-3 rounded-full text-base font-semibold hover:bg-black transition-colors shadow-lg"
                  >
                    Next Phase &rarr;
                  </button>
                </div>
              )}
            </div>
          )}

          {(gameState === "match_guess" || gameState === "match_reveal") && (
            <div className="max-w-md mx-auto text-center space-y-6 bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-1">Bonus Round!</h2>
                <p className="text-gray-500 text-sm">
                  How much does our AI think <strong>{winningMovie.title}</strong> matches your taste?
                </p>
              </div>

              <div className="w-32 mx-auto pointer-events-none">
                 <MovieCard 
                    title={winningMovie.title} 
                    movieId={winningMovie.movie_id} 
                    tmdbId={winningMovie.tmdb_id}
                 />
              </div>

              <div className="space-y-4">
                <div className="text-3xl font-black text-indigo-600">{matchGuess}%</div>
                <input 
                  type="range" min="0" max="100" 
                  value={matchGuess}
                  disabled={gameState === "match_reveal"}
                  onChange={(e) => setMatchGuess(Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                />
                <div className="flex justify-between text-xs text-gray-400 font-medium px-1">
                  <span>0% (Hate it)</span>
                  <span>100% (Love it)</span>
                </div>
              </div>

              {gameState === "match_guess" ? (
                <button 
                  onClick={handleMatchSubmit}
                  className="w-full bg-indigo-600 text-white py-3 rounded-xl font-bold hover:bg-indigo-700 transition-colors"
                >
                  Lock In Guess
                </button>
              ) : (
                <div className="bg-green-50 p-4 rounded-xl border border-green-100 animate-pulse">
                  <p className="text-green-800 font-medium text-sm mb-1">Actual Match Score</p>
                  <div className="text-4xl font-black text-green-600">{Math.round(winningMovie.match_score * 100)}%</div>
                  <p className="text-xs text-green-700 mt-2">Difference: {Math.abs(matchGuess - Math.round(winningMovie.match_score * 100))}%</p>
                  <button 
                    onClick={nextRound}
                    className="mt-4 bg-white text-green-700 border border-green-200 px-6 py-2 rounded-lg font-semibold hover:bg-green-50 w-full text-sm"
                  >
                    Next Round
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}