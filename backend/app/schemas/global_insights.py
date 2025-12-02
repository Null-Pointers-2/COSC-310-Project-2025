"""Global insights schemas for platform-wide statistics."""

from pydantic import BaseModel


class GlobalGenreStats(BaseModel):
    """Statistics for a genre across all users."""

    genre: str
    total_ratings: int  # Total number of ratings for this genre
    average_rating: float  # Average rating across all users
    user_count: int  # Number of unique users who rated this genre
    popularity_score: float  # Weighted score combining frequency and rating


class GlobalGenreLeaderboard(BaseModel):
    """Global genre popularity leaderboard."""

    genres: list[GlobalGenreStats]
    total_users: int
    total_ratings: int
