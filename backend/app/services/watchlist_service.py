"""Watchlist service."""
from typing import List
from app.repositories.watchlist_repo import WatchlistRepository
from app.repositories.movies_repo import MoviesRepository
from app.schemas.watchlist import WatchlistItem, WatchlistItemCreate

watchlist_repo = WatchlistRepository()
movies_repo = MoviesRepository()

def get_user_watchlist(user_id: str) -> List[WatchlistItem]:
    """Get user's watchlist with movie details."""
    # TODO: Get watchlist items, enrich with movie data
    pass

def add_to_watchlist(user_id: str, item: WatchlistItemCreate) -> WatchlistItem:
    """Add movie to user's watchlist."""
    # TODO: Check if already in watchlist
    # Add if not present
    pass

def remove_from_watchlist(user_id: str, movie_id: str) -> bool:
    """Remove movie from user's watchlist."""
    # TODO: Use watchlist_repo.remove()
    pass

def is_in_watchlist(user_id: str, movie_id: str) -> bool:
    """Check if movie is in user's watchlist."""
    # TODO: Use watchlist_repo.exists()
    pass