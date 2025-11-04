"""Watchlist schemas."""
from pydantic import BaseModel
from datetime import datetime

class WatchlistItemCreate(BaseModel):
    """Schema for adding movie to watchlist."""
    movie_id: int

class WatchlistItem(BaseModel):
    """Watchlist item."""
    user_id: str
    movie_id: int
  # added_at: datetime TODO: add datetime compatibility