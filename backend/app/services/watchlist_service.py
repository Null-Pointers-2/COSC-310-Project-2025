"""Watchlist service."""

from datetime import datetime

from app.schemas.watchlist import WatchlistItem, WatchlistItemCreate


def get_user_watchlist(resources, user_id: str) -> list[WatchlistItem]:
    """Get user's watchlist with correct timestamps."""
    repo_items = resources.watchlist_repo.get_by_user(user_id)

    items: list[WatchlistItem] = []
    for item in repo_items:
        movie_id = item["movie_id"]

        movie = resources.movies_repo.get_by_id(movie_id)

        if movie:
            added_at_dt = datetime.fromisoformat(item["added_at"])

            items.append(
                WatchlistItem(user_id=user_id, movie_id=movie_id, added_at=added_at_dt),
            )
    return items


def add_to_watchlist(resources, user_id: str, item: WatchlistItemCreate) -> WatchlistItem:
    """Add movie to user's watchlist."""
    movie_id = item.movie_id

    movie = resources.movies_repo.get_by_id(movie_id)
    if not movie:
        raise ValueError(f"Movie with ID {movie_id} not found.")

    if resources.watchlist_repo.exists(user_id, movie_id):
        msg = "Movie already in watchlist."
        raise ValueError(msg)

    saved_item = resources.watchlist_repo.add(user_id, movie_id)

    added_at_dt = datetime.fromisoformat(saved_item["added_at"])

    return WatchlistItem(user_id=user_id, movie_id=movie_id, added_at=added_at_dt)


def remove_from_watchlist(resources, user_id: str, movie_id: int) -> bool:
    """Remove movie from user's watchlist."""
    return resources.watchlist_repo.remove(user_id, movie_id)


def is_in_watchlist(resources, user_id: str, movie_id: int) -> bool:
    """Check if movie is in user's watchlist."""
    return resources.watchlist_repo.exists(user_id, movie_id)
