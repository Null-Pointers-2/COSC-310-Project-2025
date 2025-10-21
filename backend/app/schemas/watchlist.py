"""Watchlist schemas."""
from pydantic import BaseModel
from datetime import datetime

class WatchlistItemCreate(BaseModel):
    """Schema for adding movie to watchlist."""
    movie_id: str

class WatchlistItem(BaseModel):
    """Watchlist item."""
    id: str
    user_id: str
    movie_id: str
    added_at: datetime