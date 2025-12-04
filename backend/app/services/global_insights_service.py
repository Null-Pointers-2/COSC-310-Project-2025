"""Global insights service for platform-wide analytics."""

import logging
from collections import defaultdict
from statistics import mean

from app.schemas.global_insights import GlobalGenreLeaderboard, GlobalGenreStats

logger = logging.getLogger(__name__)


def _calculate_popularity_score(total_ratings: int, avg_rating: float, total_platform_ratings: int) -> float:
    """
    Calculate popularity score (0-100) based on frequency and rating.

    Formula: (frequency_weight * 40) + (rating_weight * 60)
    - Frequency: How often this genre is rated across all users (0-40 points)
    - Rating: How highly rated (0-60 points)
    """
    if total_platform_ratings == 0:
        return 0.0

    frequency_weight = min(total_ratings / max(total_platform_ratings, 1), 1.0)
    rating_weight = (avg_rating - 0.5) / 4.5

    score = (frequency_weight * 40) + (rating_weight * 60)
    return round(score, 2)


def get_global_genre_leaderboard(resources) -> GlobalGenreLeaderboard:
    """
    Generate global genre popularity leaderboard across all users.

    Args:
        resources: SingletonResources instance

    Returns:
        GlobalGenreLeaderboard with ranked genres
    """
    all_users = resources.users_repo.get_all()
    user_ids = [user["id"] for user in all_users]

    genre_stats = defaultdict(lambda: {"ratings": [], "user_ids": set()})

    total_platform_ratings = 0

    for user_id in user_ids:
        user_ratings = resources.ratings_repo.get_by_user(user_id)

        for rating in user_ratings:
            movie = resources.movies_repo.get_by_id(rating["movie_id"])
            if not movie or not movie.get("genres"):
                continue

            rating_value = float(rating["rating"])
            total_platform_ratings += 1

            for genre in movie["genres"]:
                if not genre:
                    continue

                genre_stats[genre]["ratings"].append(rating_value)
                genre_stats[genre]["user_ids"].add(user_id)

    genre_leaderboard = []

    for genre, stats in genre_stats.items():
        total_ratings = len(stats["ratings"])
        avg_rating = mean(stats["ratings"]) if stats["ratings"] else 0.0
        user_count = len(stats["user_ids"])

        popularity_score = _calculate_popularity_score(total_ratings, avg_rating, total_platform_ratings)

        genre_leaderboard.append(
            GlobalGenreStats(
                genre=genre,
                total_ratings=total_ratings,
                average_rating=round(avg_rating, 2),
                user_count=user_count,
                popularity_score=popularity_score,
            )
        )

    genre_leaderboard.sort(key=lambda x: x.popularity_score, reverse=True)

    return GlobalGenreLeaderboard(
        genres=genre_leaderboard,
        total_users=len(user_ids),
        total_ratings=total_platform_ratings,
    )
