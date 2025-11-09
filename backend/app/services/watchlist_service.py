"""Watchlist service."""
from datetime import datetime
from typing import List
from app.repositories.watchlist_repo import WatchlistRepository
from app.repositories.movies_repo import MoviesRepository
from app.schemas.watchlist import WatchlistItem, WatchlistItemCreate

watchlist_repo = WatchlistRepository()
movies_repo = MoviesRepository()


def get_user_watchlist(user_id: str) -> List[WatchlistItem]:
    """Get user's watchlist with movie details."""
    movie_ids = watchlist_repo.get_by_user(user_id)
    if not movie_ids:
        return []

    items: List[WatchlistItem] = []
    for movie_id in movie_ids:
        movie = movies_repo.get_by_id(movie_id)
        if movie:
            items.append(
                WatchlistItem(
                    user_id=user_id,
                    movie_id=movie_id,
                #   added_at=datetime.now(), TODO: add datetime compatibility later
                )
            )
    return items


def add_to_watchlist(user_id: str, item: WatchlistItemCreate) -> WatchlistItem:
    """Add movie to user's watchlist."""
    movie_id = item.movie_id

    movie = movies_repo.get_by_id(movie_id)
    if not movie:
        raise ValueError(f"Movie with ID {movie_id} not found.")

    if watchlist_repo.exists(user_id, movie_id):
        raise ValueError("Movie already in watchlist.")

    watchlist_repo.add(user_id, movie_id)

    return WatchlistItem(
        user_id=user_id,
        movie_id=movie_id,
     #  added_at=datetime.now(), TODO: add datetime compatibility later
    )


def remove_from_watchlist(user_id: str, movie_id: int) -> bool:
    """Remove movie from user's watchlist."""
    return watchlist_repo.remove(user_id, movie_id)


def is_in_watchlist(user_id: str, movie_id: int) -> bool:
    """Check if movie is in user's watchlist."""
    return watchlist_repo.exists(user_id, movie_id)
