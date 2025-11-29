"""User insights service with analytics algorithms."""

import logging
from collections import defaultdict
from datetime import UTC, datetime
from statistics import mean, stdev

from app.schemas.user_insights import (
    GenreInsight,
    ThemeInsight,
    UserInsights,
    UserInsightsSummary,
    WatchlistMetrics,
)

logger = logging.getLogger(__name__)


def _calculate_preference_score(count: int, avg_rating: float, total_count: int) -> float:
    """
    Calculate preference score (0-100) based on frequency and rating.

    Formula: (frequency_weight * 40) + (rating_weight * 60)
    - Frequency: How often this appears (0-40 points)
    - Rating: How highly rated (0-60 points)
    """
    if total_count == 0:
        return 0.0

    frequency_weight = min(count / max(total_count, 1), 1.0)  # 0-1
    rating_weight = (avg_rating - 0.5) / 4.5  # Normalize 0.5-5.0 to 0-1

    score = (frequency_weight * 40) + (rating_weight * 60)
    return round(score, 2)


def _analyze_genres(resources, user_id: str) -> tuple[str | None, list[str], list[GenreInsight]]:
    """
    Analyze user's genre preferences.

    Returns: (top_genre, top_3_genres, genre_insights)
    """
    # Get all user ratings
    all_ratings = resources.ratings_repo.get_by_user(user_id)
    watchlist_items = resources.watchlist_repo.get_by_user(user_id)

    if not all_ratings:
        return None, [], []

    # Get watchlist movie IDs
    watchlist_movie_ids = {item["movie_id"] for item in watchlist_items}

    # Build genre statistics
    genre_stats = defaultdict(lambda: {"total": 0, "watchlist": 0, "ratings": [], "watchlist_ratings": []})

    for rating in all_ratings:
        movie = resources.movies_repo.get_by_id(rating["movie_id"])
        if not movie or not movie.get("genres"):
            continue

        is_watchlist = rating["movie_id"] in watchlist_movie_ids
        rating_value = float(rating["rating"])

        # Process each genre for this movie
        for genre in movie["genres"]:
            if not genre:  # Skip empty genres
                continue

            genre_stats[genre]["total"] += 1
            genre_stats[genre]["ratings"].append(rating_value)

            if is_watchlist:
                genre_stats[genre]["watchlist"] += 1
                genre_stats[genre]["watchlist_ratings"].append(rating_value)

    # Convert to GenreInsight objects
    genre_insights = []
    total_ratings = len(all_ratings)

    for genre, stats in genre_stats.items():
        avg_rating = mean(stats["ratings"]) if stats["ratings"] else 0.0
        watchlist_avg_rating = mean(stats["watchlist_ratings"]) if stats["watchlist_ratings"] else 0.0

        preference_score = _calculate_preference_score(stats["total"], avg_rating, total_ratings)

        genre_insights.append(
            GenreInsight(
                genre=genre,
                total_rated=stats["total"],
                watchlist_rated=stats["watchlist"],
                average_rating=round(avg_rating, 2),
                watchlist_average_rating=round(watchlist_avg_rating, 2),
                preference_score=preference_score,
            )
        )

    # Sort by preference score
    genre_insights.sort(key=lambda x: x.preference_score, reverse=True)

    # Extract top genres
    top_genre = genre_insights[0].genre if genre_insights else None
    top_3_genres = [g.genre for g in genre_insights[:3]]

    return top_genre, top_3_genres, genre_insights


def _analyze_themes(resources, user_id: str) -> tuple[str | None, list[str], list[ThemeInsight]]:
    """
    Analyze user's theme preferences using genome data.

    Returns: (top_theme, top_5_themes, theme_insights)
    """
    # Get highly-rated movies (4.0+)
    all_ratings = resources.ratings_repo.get_by_user(user_id)
    high_rated_movies = [r for r in all_ratings if float(r["rating"]) >= 4.0]

    if not high_rated_movies:
        return None, [], []

    movie_ids = [r["movie_id"] for r in high_rated_movies]

    # Get top tags for these movies
    top_tags = resources.genome_repo.get_top_tags_for_movies(movie_ids, top_n=20, min_relevance=0.5)

    if not top_tags:
        return None, [], []

    # Build theme insights
    theme_insights = []
    total_movies = len(high_rated_movies)

    for tag_data in top_tags:
        # Calculate average rating for movies with this tag
        tag_movie_ratings = []
        for rating in high_rated_movies:
            # Check if this movie has this tag with high relevance
            movie_tags = resources.genome_repo.get_movie_tags(rating["movie_id"], min_relevance=0.5)
            if any(t["tag_id"] == tag_data["tag_id"] for t in movie_tags):
                tag_movie_ratings.append(float(rating["rating"]))

        if not tag_movie_ratings:
            continue

        avg_rating = mean(tag_movie_ratings)
        preference_score = _calculate_preference_score(len(tag_movie_ratings), avg_rating, total_movies)

        theme_insights.append(
            ThemeInsight(
                tag=tag_data["tag"],
                tag_id=tag_data["tag_id"],
                movies_count=tag_data["movie_count"],
                average_relevance=round(tag_data["avg_relevance"], 3),
                average_rating=round(avg_rating, 2),
                preference_score=preference_score,
            )
        )

    # Sort by preference score
    theme_insights.sort(key=lambda x: x.preference_score, reverse=True)

    # Extract top themes
    top_theme = theme_insights[0].tag if theme_insights else None
    top_5_themes = [t.tag for t in theme_insights[:5]]

    return top_theme, top_5_themes, theme_insights


def _analyze_watchlist_metrics(resources, user_id: str) -> WatchlistMetrics:
    """
    Analyze watchlist completion and engagement metrics.

    Returns: WatchlistMetrics
    """
    watchlist_items = resources.watchlist_repo.get_by_user(user_id)
    all_ratings = resources.ratings_repo.get_by_user(user_id)

    total_watchlist = len(watchlist_items)

    if total_watchlist == 0:
        return WatchlistMetrics(
            total_watchlist_items=0,
            items_rated=0,
            items_not_rated=0,
            completion_rate=0.0,
            average_rating=None,
            average_time_to_rate_hours=None,
            genres_in_watchlist=[],
            most_common_watchlist_genre=None,
        )

    # Find which watchlist items were rated
    watchlist_movie_ids = {item["movie_id"]: item for item in watchlist_items}
    rated_watchlist_items = []
    time_deltas = []

    for rating in all_ratings:
        if rating["movie_id"] in watchlist_movie_ids:
            watchlist_item = watchlist_movie_ids[rating["movie_id"]]
            rated_watchlist_items.append(rating)

            # Calculate time to rate
            try:
                added_at = datetime.fromisoformat(watchlist_item["added_at"].replace("Z", "+00:00"))
                rated_at = datetime.fromisoformat(rating["timestamp"].replace("Z", "+00:00"))
                delta_hours = (rated_at - added_at).total_seconds() / 3600
                if delta_hours >= 0:  # Only positive deltas (rated after adding)
                    time_deltas.append(delta_hours)
            except (ValueError, KeyError):
                pass

    items_rated = len(rated_watchlist_items)
    items_not_rated = total_watchlist - items_rated
    completion_rate = (items_rated / total_watchlist) * 100 if total_watchlist > 0 else 0.0

    # Calculate average rating for completed items
    avg_rating = None
    if rated_watchlist_items:
        avg_rating = round(mean(float(r["rating"]) for r in rated_watchlist_items), 2)

    # Calculate average time to rate
    avg_time = None
    if time_deltas:
        avg_time = round(mean(time_deltas), 2)

    # Analyze genres in watchlist
    genres_in_watchlist = set()
    genre_counts = defaultdict(int)

    for item in watchlist_items:
        movie = resources.movies_repo.get_by_id(item["movie_id"])
        if movie and movie.get("genres"):
            for genre in movie["genres"]:
                if genre:
                    genres_in_watchlist.add(genre)
                    genre_counts[genre] += 1

    most_common_genre = max(genre_counts.items(), key=lambda x: x[1])[0] if genre_counts else None

    return WatchlistMetrics(
        total_watchlist_items=total_watchlist,
        items_rated=items_rated,
        items_not_rated=items_not_rated,
        completion_rate=round(completion_rate, 2),
        average_rating=avg_rating,
        average_time_to_rate_hours=avg_time,
        genres_in_watchlist=sorted(genres_in_watchlist),
        most_common_watchlist_genre=most_common_genre,
    )


def generate_user_insights(resources, user_id: str, force_refresh: bool = False) -> UserInsights | None:
    """
    Generate comprehensive insights for a user.

    Args:
        resources: SingletonResources instance
        user_id: The user ID
        force_refresh: If True, regenerate even if cached

    Returns:
        UserInsights object or None if user not found
    """
    # Check if user exists
    user = resources.users_repo.get_by_id(user_id)
    if not user:
        logger.warning(f"User {user_id} not found")
        return None

    # Check for cached insights (unless force refresh)
    if not force_refresh:
        cached = resources.user_insights_repo.get_by_user_id(user_id)
        if cached:
            logger.info(f"Returning cached insights for user {user_id}")
            return UserInsights(**cached)

    logger.info(f"Generating fresh insights for user {user_id}")

    # Get all ratings for overall stats
    all_ratings = resources.ratings_repo.get_by_user(user_id)
    total_ratings = len(all_ratings)

    avg_rating = None
    rating_consistency = None

    if all_ratings:
        ratings_values = [float(r["rating"]) for r in all_ratings]
        avg_rating = round(mean(ratings_values), 2)

        if len(ratings_values) > 1:
            rating_consistency = round(stdev(ratings_values), 2)

    # Analyze genres
    top_genre, top_3_genres, genre_insights = _analyze_genres(resources, user_id)

    # Analyze themes (genome data)
    top_theme, top_5_themes, theme_insights = _analyze_themes(resources, user_id)

    # Analyze watchlist metrics
    watchlist_metrics = _analyze_watchlist_metrics(resources, user_id)

    # Create insights object
    insights = UserInsights(
        user_id=user_id,
        generated_at=datetime.now(UTC),
        top_genre=top_genre,
        top_3_genres=top_3_genres,
        genre_insights=genre_insights,
        top_theme=top_theme,
        top_5_themes=top_5_themes,
        theme_insights=theme_insights,
        watchlist_metrics=watchlist_metrics,
        total_ratings=total_ratings,
        average_rating=avg_rating,
        rating_consistency=rating_consistency,
    )

    # Cache the insights
    insights_dict = insights.model_dump(mode="json")
    resources.user_insights_repo.save(insights_dict)

    logger.info(f"Insights generated and cached for user {user_id}")
    return insights


def get_user_insights_summary(resources, user_id: str) -> UserInsightsSummary | None:
    """
    Get simplified insights summary for a user.

    Args:
        resources: SingletonResources instance
        user_id: The user ID

    Returns:
        UserInsightsSummary or None
    """
    insights = generate_user_insights(resources, user_id, force_refresh=False)
    if not insights:
        return None

    return UserInsightsSummary(
        user_id=insights.user_id,
        top_genre=insights.top_genre,
        top_3_genres=insights.top_3_genres,
        top_theme=insights.top_theme,
        top_5_themes=insights.top_5_themes,
        watchlist_completion_rate=insights.watchlist_metrics.completion_rate,
        total_ratings=insights.total_ratings,
        generated_at=insights.generated_at,
    )
