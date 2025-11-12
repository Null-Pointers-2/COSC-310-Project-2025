"""Recommendations service using cosine similarity."""

from collections import defaultdict

from app.schemas.recommendation import RecommendationItem, RecommendationList


def get_recommendations(resources, user_id: str, limit: int = 10, force_refresh: bool = False) -> RecommendationList:
    """
    Get personalized recommendations for a user.

    Uses cached recommendations if available and fresh,
    otherwise generates new recommendations.

    Args:
        resources: Application resources singleton
        user_id: User ID to generate recommendations for
        limit: Maximum number of recommendations to return
        force_refresh: Force regeneration even if cached recommendations exist

    Returns:
        RecommendationList with personalized recommendations
    """
    if not force_refresh:
        cached = resources.recommendations_repo.get_for_user(user_id)
        if cached and resources.recommendations_repo.is_fresh(user_id, max_age_hours=24):
            items = [RecommendationItem(**item) for item in cached.get("recommendations", [])[:limit]]
            return RecommendationList(user_id=user_id, recommendations=items)

    recommendations = generate_recommendations(resources, user_id, limit)
    resources.recommendations_repo.save_for_user(user_id, [item.model_dump() for item in recommendations])

    return RecommendationList(user_id=user_id, recommendations=recommendations)


def generate_recommendations(resources, user_id: str, limit: int = 10) -> list[RecommendationItem]:
    """
    Generate new recommendations using cosine similarity.

    Args:
        resources: Application resources singleton
        user_id: User ID to generate recommendations for
        limit: Number of recommendations to generate

    Returns:
        List of RecommendationItem sorted by similarity score
    """

    user_ratings = resources.ratings_repo.get_by_user(user_id)

    if not user_ratings:
        return _get_fallback_recommendations(resources, limit)

    seed_movies = [r for r in user_ratings if r["rating"] >= 4.0]

    if not seed_movies:
        seed_movies = sorted(user_ratings, key=lambda x: x["rating"], reverse=True)[:5]

    rated_movie_ids = {r["movie_id"] for r in user_ratings}
    recommendation_scores: dict[int, list[float]] = defaultdict(list)

    for seed_rating in seed_movies:
        movie_id = seed_rating["movie_id"]
        movie = resources.movies_repo.get_by_id(movie_id)

        if not movie:
            continue

        similar_movies = get_similar_movies(resources, movie_id, limit)

        user_rating_weight = seed_rating["rating"] / 5.0  # Normalize to 0-1

        for rec in similar_movies:
            # Don't recommend movies user has already rated
            if rec.movie_id not in rated_movie_ids:
                weighted_score = rec.similarity_score * user_rating_weight
                recommendation_scores[rec.movie_id].append(weighted_score)

    final_recommendations = []
    for movie_id, scores in recommendation_scores.items():
        avg_score = sum(scores) / len(scores)
        final_recommendations.append(RecommendationItem(movie_id=movie_id, similarity_score=round(avg_score, 4)))

    final_recommendations.sort(key=lambda x: x.similarity_score, reverse=True)

    return final_recommendations[:limit]


def get_similar_movies(resources, movie_id: int, limit: int = 10) -> list[RecommendationItem]:
    """
    Get movies similar to a given movie.

    Args:
        resources: Application resources singleton
        movie_id: Movie ID to find similar movies for
        limit: Number of similar movies to return

    Returns:
        List of RecommendationItem sorted by similarity score
    """

    movie = resources.movies_repo.get_by_id(movie_id)
    if not movie:
        return []

    recommendations = resources.recommender.get_similar_by_id(movie_id, n=limit)

    if recommendations is None:
        print(f"Warning: Movie ID {movie_id} not found in recommender dataset")
        return []

    result = []
    for rec_id, score in recommendations:
        movie = resources.movies_repo.get_by_id(rec_id)
        if movie:
            result.append(RecommendationItem(movie_id=rec_id, similarity_score=round(float(score), 4)))
        else:
            print(f"Warning: Recommended movie ID {rec_id} not found in movies repository")

    return result


def _get_fallback_recommendations(resources, limit: int = 10) -> list[RecommendationItem]:
    """
    Get fallback recommendations for users with no ratings.

    Returns popular movies or a curated selection.

    Args:
        resources: Application resources singleton
        limit: Number of recommendations to return

    Returns:
        List of RecommendationItem with default similarity scores
    """
    # Get first N movies as fallback
    movies = resources.movies_repo.get_all(limit=limit)

    return [
        RecommendationItem(
            movie_id=movie["movieId"],
            similarity_score=0.5,  # Neutral score for fallback recommendations
        )
        for movie in movies
    ]


def refresh_recommendations_for_user(resources, user_id: str, limit: int = 10) -> RecommendationList:
    """
    Force refresh recommendations for a user.

    Convenience method that calls get_recommendations with force_refresh=True.

    Args:
        resources: Application resources singleton
        user_id: User ID to refresh recommendations for
        limit: Number of recommendations to generate

    Returns:
        RecommendationList with fresh recommendations
    """
    return get_recommendations(resources, user_id, limit=limit, force_refresh=True)


def clear_recommendations_cache(resources, user_id: str) -> None:
    """
    Clear cached recommendations for a user.

    Args:
        resources: Application resources singleton
        user_id: User ID to clear cache for
    """
    resources.recommendations_repo.clear_for_user(user_id)
