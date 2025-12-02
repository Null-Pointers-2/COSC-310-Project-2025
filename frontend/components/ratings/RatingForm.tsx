"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/../hooks/auth/useAuth";

interface RatingFormProps {
  movieId: number | string;
  onRateSuccess?: (newRating: number) => void;
}

interface Rating {
  id: number;
  movie_id: number;
  rating: number;
}

export function RatingForm({ movieId, onRateSuccess }: RatingFormProps) {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [existingRatingId, setExistingRatingId] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const router = useRouter();
  const { authFetch, isAuthenticated } = useAuth();

  const displayRating = hoverRating > 0 ? hoverRating : rating;

  useEffect(() => {
    const checkExistingRating = async () => {
      if (!isAuthenticated) {
        setIsLoading(false);
        return;
      }

      try {
        const res = await authFetch("/ratings/me");
        if (res.ok) {
          const myRatings: Rating[] = await res.json();
          const match = myRatings.find((r) => r.movie_id === Number(movieId));
          
          if (match) {
            setRating(match.rating);
            setExistingRatingId(match.id);
          }
        }
      } catch (err) {
        console.error("Failed to check ratings", err);
      } finally {
        setIsLoading(false);
      }
    };

    checkExistingRating();

  }, [movieId, isAuthenticated]); // eslint-disable-line

  const handleSubmit = async () => {
    if (rating === 0) return;

    setIsSubmitting(true);
    setError(null);

    try {

      let response;
      
      if (existingRatingId) {
        response = await authFetch(`/ratings/${existingRatingId}`, {
          method: "PUT",
          body: JSON.stringify({ rating: rating }),
        });
      } else {
        response = await authFetch(`/ratings`, {
          method: "POST",
          body: JSON.stringify({
            movie_id: movieId,
            rating: rating,
          }),
        });
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to submit rating");
      }

      if (!existingRatingId) {
        const newRatingData = await response.json();
        setExistingRatingId(newRatingData.id);
      }

      if (onRateSuccess) {
        onRateSuccess(rating);
      }
      
      router.refresh();

    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return <div className="h-24 bg-gray-50 rounded-lg animate-pulse" />;
  }

  return (
    <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm max-w-sm">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">
        {existingRatingId ? "Your Rating" : "Rate this movie"}
      </h3>

      <div 
        className="flex items-center gap-1 mb-4" 
        onMouseLeave={() => setHoverRating(0)}
      >
        {[1, 2, 3, 4, 5].map((starIndex) => {
          const filledValue = starIndex; 
          const halfValue = starIndex - 0.5;
          
          return (
            <div key={starIndex} className="relative cursor-pointer group">
              {/* Base Star SVG */}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                className={`w-8 h-8 transition-colors duration-150 ${
                  displayRating >= filledValue
                    ? "text-yellow-400 fill-yellow-400"
                    : displayRating >= halfValue
                    ? "text-yellow-400 fill-yellow-400"
                    : "text-gray-300 fill-transparent"
                }`}
                stroke="currentColor"
                strokeWidth={1.5}
              >
                 <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.545.044.739.76.292 1.133l-4.25 3.505a.562.562 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.25-3.505a.562.562 0 01.292-1.133l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                 
                 {/* Clip Path for visual half star */}
                 {displayRating === halfValue && (
                   <defs>
                     <clipPath id={`half-star-${starIndex}`}>
                       <rect x="0" y="0" width="12" height="24" />
                     </clipPath>
                   </defs>
                 )}
              </svg>

              {/* Half Star Overlay (not working yet)*/}
              {displayRating === halfValue && (
                 <svg
                 xmlns="http://www.w3.org/2000/svg"
                 viewBox="0 0 24 24"
                 className="w-8 h-8 absolute top-0 left-0 text-yellow-400 fill-yellow-400 pointer-events-none"
                 stroke="currentColor"
                 strokeWidth={1.5}
               >
                 <clipPath id={`clip-${starIndex}`}>
                    <rect x="0" y="0" width="12" height="24" />
                 </clipPath>
                 <path clipPath={`url(#clip-${starIndex})`} strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.545.044.739.76.292 1.133l-4.25 3.505a.562.562 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.25-3.505a.562.562 0 01.292-1.133l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
               </svg>
              )}

              {/* Touch/Click Targets */}
              <div className="absolute inset-0 flex">
                <div 
                  className="w-1/2 h-full z-10" 
                  onMouseEnter={() => setHoverRating(halfValue)}
                  onClick={() => setRating(halfValue)}
                  title={`${halfValue} Stars`}
                />
                <div 
                  className="w-1/2 h-full z-10" 
                  onMouseEnter={() => setHoverRating(filledValue)}
                  onClick={() => setRating(filledValue)}
                  title={`${filledValue} Stars`}
                />
              </div>
            </div>
          );
        })}
        <span className="ml-2 text-sm font-medium text-gray-600 min-w-[2rem]">
          {displayRating > 0 ? displayRating.toFixed(1) : "0.0"}
        </span>
      </div>

      {error && (
        <p className="text-xs text-red-500 mb-3 bg-red-50 p-2 rounded">
          {error}
        </p>
      )}

      <button
        onClick={handleSubmit}
        disabled={isSubmitting || rating === 0}
        className={`
          w-full py-2 px-4 rounded-lg text-sm font-medium transition-colors
          ${rating === 0 
            ? "bg-gray-100 text-gray-400 cursor-not-allowed" 
            : "bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm hover:shadow"
          }
        `}
      >
        {isSubmitting ? "Submitting..." : (existingRatingId ? "Update Rating" : "Submit Rating")}
      </button>
    </div>
  );
}