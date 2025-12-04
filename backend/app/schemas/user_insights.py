"""User insights schemas for analytics and preferences."""

from datetime import datetime

from pydantic import BaseModel


class GenreInsight(BaseModel):
    """Insights for a specific genre."""

    genre: str
    total_rated: int
    watchlist_rated: int
    average_rating: float
    watchlist_average_rating: float
    preference_score: float


class ThemeInsight(BaseModel):
    """Insights for a specific theme/tag from genome data."""

    tag: str
    tag_id: int
    movies_count: int
    average_relevance: float
    average_rating: float
    preference_score: float


class WatchlistMetrics(BaseModel):
    """Watchlist completion and engagement metrics."""

    total_watchlist_items: int
    items_rated: int
    items_not_rated: int
    completion_rate: float
    average_rating: float | None
    average_time_to_rate_hours: float | None
    genres_in_watchlist: list[str]
    most_common_watchlist_genre: str | None


class UserInsights(BaseModel):
    """Complete user insights and analytics."""

    user_id: str
    generated_at: datetime

    top_genre: str | None
    top_3_genres: list[str]
    genre_insights: list[GenreInsight]

    top_theme: str | None
    top_5_themes: list[str]
    theme_insights: list[ThemeInsight]

    watchlist_metrics: WatchlistMetrics

    total_ratings: int
    average_rating: float | None
    rating_consistency: float | None


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
