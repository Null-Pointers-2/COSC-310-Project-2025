"""Global insights schemas for platform-wide statistics."""

from pydantic import BaseModel


class GlobalGenreStats(BaseModel):
    """Statistics for a genre across all users."""

    genre: str
    total_ratings: int
    average_rating: float
    user_count: int
    popularity_score: float


class GlobalGenreLeaderboard(BaseModel):
    """Global genre popularity leaderboard."""

    genres: list[GlobalGenreStats]
    total_users: int
    total_ratings: int
