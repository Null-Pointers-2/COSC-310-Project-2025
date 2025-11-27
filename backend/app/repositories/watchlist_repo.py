"""Repository for user watchlist operations."""

import json
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings


class WatchlistRepository:
    """Handle user watchlists stored in JSON."""

    def __init__(self, watchlist_file: str | None = None):
        """Initialize with path to watchlist JSON file."""
        if watchlist_file is None:
            watchlist_file = settings.WATCHLIST_FILE
        self.watchlist_file = Path(watchlist_file)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create watchlist file if it doesn't exist."""
        try:
            if not self.watchlist_file.exists():
                self.watchlist_file.parent.mkdir(parents=True, exist_ok=True)
                self.watchlist_file.write_text("[]")
        except OSError as e:
            raise OSError(f"Failed to initialize watchlist file: {e}") from e

    def _read(self) -> list[dict]:
        """Read all watchlist items."""
        try:
            content = self.watchlist_file.read_text()
            return json.loads(content)
        except (OSError, json.JSONDecodeError):
            return []

    def _write(self, data: list[dict]):
        """Write all watchlist items to file."""
        try:
            with self.watchlist_file.open("w") as f:
                json.dump(data, f, indent=4)
        except OSError as e:
            raise OSError(f"Failed to write watchlist file: {e}") from e

    def get_by_user(self, user_id: str) -> list[dict]:
        """Get user's watchlist."""
        data = self._read()
        return [item for item in data if item["user_id"] == user_id]

    def add(self, user_id: str, movie_id: int) -> dict:
        """Add movie to user's watchlist."""
        data = self._read()
        user_id = str(user_id)
        movie_id = int(movie_id)

        existing = next((item for item in data if item["user_id"] == user_id and item["movie_id"] == movie_id), None)

        if existing:
            return existing

        new_item = {"user_id": user_id, "movie_id": movie_id, "added_at": datetime.now(timezone.utc).isoformat()}

        data.append(new_item)
        self._write(data)

        return new_item

    def remove(self, user_id: str, movie_id: int) -> bool:
        """Remove movie from user's watchlist."""
        data = self._read()
        user_id = str(user_id)
        movie_id = int(movie_id)

        new_data = [item for item in data if not (item["user_id"] == user_id and item["movie_id"] == movie_id)]

        if len(new_data) < len(data):
            self._write(new_data)
            return True

        return False

    def exists(self, user_id: str, movie_id: int) -> bool:
        """Check if movie is in user's watchlist."""
        data = self._read()
        movie_id = int(movie_id)
        return any(item["user_id"] == user_id and item["movie_id"] == movie_id for item in data)

    def save_data(self, data: list[dict]):
        """Overwrite the watchlist file with the given list."""
        self._write(data)
