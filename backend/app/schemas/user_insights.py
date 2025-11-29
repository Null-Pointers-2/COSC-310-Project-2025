"""User insights schemas for analytics and preferences."""

from datetime import datetime

from pydantic import BaseModel


class GenreInsight(BaseModel):
    """Insights for a specific genre."""

    genre: str
    total_rated: int  # Total movies rated in this genre
    watchlist_rated: int  # Movies rated from watchlist in this genre
    average_rating: float  # Overall average rating for this genre
    watchlist_average_rating: float  # Average rating for watchlist movies
    preference_score: float  # Weighted score (0-100) combining frequency and rating


class ThemeInsight(BaseModel):
    """Insights for a specific theme/tag from genome data."""

    tag: str
    tag_id: int
    movies_count: int  # Number of highly-rated movies with this tag
    average_relevance: float  # Average relevance score for this tag
    average_rating: float  # Average user rating for movies with this tag
    preference_score: float  # Weighted preference score


class WatchlistMetrics(BaseModel):
    """Watchlist completion and engagement metrics."""

    total_watchlist_items: int
    items_rated: int
    items_not_rated: int
    completion_rate: float  # Percentage (0-100)
    average_rating: float | None  # Average rating for completed watchlist items
    average_time_to_rate_hours: float | None  # Avg hours between add and rate
    genres_in_watchlist: list[str]  # Unique genres in watchlist
    most_common_watchlist_genre: str | None


class UserInsights(BaseModel):
    """Complete user insights and analytics."""

    user_id: str
    generated_at: datetime

    # Favorite Genres
    top_genre: str | None
    top_3_genres: list[str]
    genre_insights: list[GenreInsight]

    # Favorite Themes (from genome data)
    top_theme: str | None
    top_5_themes: list[str]
    theme_insights: list[ThemeInsight]

    # Watchlist Metrics
    watchlist_metrics: WatchlistMetrics

    # Overall Stats
    total_ratings: int
    average_rating: float | None
    rating_consistency: float | None  # Std deviation (lower = more consistent)


class UserInsightsSummary(BaseModel):
    """Simplified user insights summary."""

    user_id: str
    top_genre: str | None
    top_3_genres: list[str]
    top_theme: str | None
    top_5_themes: list[str]
    watchlist_completion_rate: float
    total_ratings: int
    generated_at: datetime
