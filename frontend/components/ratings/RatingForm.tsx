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

  }, [movieId, isAuthenticated, authFetch]);

  const saveRating = async (newRating: number) => {
    setIsSubmitting(true);
    setError(null);

    try {
      let response;

      if (existingRatingId) {
        response = await authFetch(`/ratings/${existingRatingId}`, {
          method: "PUT",
          body: JSON.stringify({ rating: newRating }),
        });
      } else {
        response = await authFetch(`/ratings`, {
          method: "POST",
          body: JSON.stringify({
            movie_id: movieId,
            rating: newRating,
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

      setRating(newRating);

      if (onRateSuccess) {
        onRateSuccess(newRating);
      }

      router.refresh();

    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRate = (value: number) => {
    if (isSubmitting) return;
    saveRating(value);
  };

  const handleDelete = async () => {
    if (!existingRatingId || isSubmitting) return;

    setIsSubmitting(true);
    try {
      const response = await authFetch(`/ratings/${existingRatingId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete rating");
      }

      setRating(0);
      setExistingRatingId(null);
      router.refresh();
    } catch (err) {
      console.error(err);
      setError("Failed to delete rating");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return <div className="h-24 bg-gray-50 rounded-lg animate-pulse" />;
  }

  return (
    <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm max-w-sm">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-sm font-semibold text-gray-700">
          {existingRatingId ? "Your Rating" : "Rate this movie"}
        </h3>
        {existingRatingId && (
          <button
            onClick={handleDelete}
            disabled={isSubmitting}
            className="text-gray-400 hover:text-red-500 transition-colors p-1 rounded-full hover:bg-red-50 cursor-pointer"
            title="Remove rating"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
              <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
            </svg>
          </button>
        )}
      </div>

      <div
        className="flex items-center"
        onMouseLeave={() => setHoverRating(0)}
      >
        <div className="flex items-center px-0.5">
          {[1, 2, 3, 4, 5].map((starIndex) => {
            const filledValue = starIndex;
            const halfValue = starIndex - 0.5;

            const isBaseFilled = displayRating >= filledValue;

            return (
              <div key={starIndex} className="relative cursor-pointer group">
                {/* Base Star SVG */}
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  className={`w-8 h-8 transition-colors duration-150 ${
                    isBaseFilled
                      ? "text-yellow-400 fill-yellow-400"
                      : "text-gray-300 fill-transparent"
                  }`}
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.545.044.739.76.292 1.133l-4.25 3.505a.562.562 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.25-3.505a.562.562 0 01.292-1.133l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                </svg>

                {/* Half Star Overlay */}
                {displayRating === halfValue && (
                  <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  className="w-8 h-8 absolute top-0 left-0 text-yellow-400 fill-yellow-400 pointer-events-none"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <defs>
                    <clipPath id={`clip-${starIndex}`}>
                      <rect x="0" y="0" width="12" height="24" />
                    </clipPath>
                  </defs>
                  <path clipPath={`url(#clip-${starIndex})`} strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.545.044.739.76.292 1.133l-4.25 3.505a.562.562 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.25-3.505a.562.562 0 01.292-1.133l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                </svg>
                )}

                <div className="absolute inset-0 flex">
                  <div
                    className="w-1/2 h-full z-10"
                    onMouseEnter={() => setHoverRating(halfValue)}
                    onClick={() => handleRate(halfValue)}
                    title={`${halfValue} Stars`}
                  />
                  <div
                    className="w-1/2 h-full z-10"
                    onMouseEnter={() => setHoverRating(filledValue)}
                    onClick={() => handleRate(filledValue)}
                    title={`${filledValue} Stars`}
                  />
                </div>
              </div>
            );
          })}
        </div>
        <span className="ml-2 text-sm font-medium text-gray-600 min-w-[2rem]">
          {displayRating > 0 ? displayRating.toFixed(1) : "0.0"}
        </span>
      </div>

      {error && (
        <p className="text-xs text-red-500 mt-2 bg-red-50 p-2 rounded">
          {error}
        </p>
      )}
    </div>
  );
}
