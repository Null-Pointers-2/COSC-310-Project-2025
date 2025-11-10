"""Repository for user watchlist operations."""
import json
from typing import List, Optional, Dict
from pathlib import Path
from app.core.config import settings

class WatchlistRepository:
    """Handle user watchlists stored in JSON."""
    
    def __init__(self, watchlist_file: Optional[str] = None):
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
                self.watchlist_file.write_text("{}")
        except OSError as e:
            raise Exception(f"Failed to initialize watchlist file: {e}") from e
    
    def _read(self) -> Dict[str, List[int]]:
        """Read all watchlist items."""
        try:
            content = self.watchlist_file.read_text()
            return json.loads(content)
        except (IOError, json.JSONDecodeError):
            return {}
    
    def _write(self, data: Dict[str, List[int]]):
        """Write all watchlist items to file."""
        try:
            with self.watchlist_file.open("w") as f:
                json.dump(data, f, indent=4)
        except OSError as e:
            raise Exception(f"Failed to write watchlist file: {e}") from e
    
    def get_by_user(self, user_id: str) -> List[int]:
        """Get user's watchlist."""
        data = self._read()
        return data.get(str(user_id), [])
    
    def add(self, user_id: str, movie_id: int) -> Dict:
        """Add movie to user's watchlist."""
        data = self._read()
        user_key = str(user_id)
        movie_id = int(movie_id)

        if user_key not in data:
            data[user_key] = []
        
        if movie_id not in data[user_key]:
            data[user_key].append(movie_id)
            self._write(data)
        
        return {"user_id": user_id, "movie_id": movie_id}
    
    def remove(self, user_id: str, movie_id: int) -> bool:
        """Remove movie from user's watchlist."""
        data = self._read()
        user_key = str(user_id)
        movie_id = int(movie_id)

        if user_key in data and movie_id in data[user_key]:
            data[user_key].remove(movie_id)
            self._write(data)
            return True
        return False
    
    def exists(self, user_id: str, movie_id: int) -> bool:
        """Check if movie is in user's watchlist."""
        data = self._read()
        movie_id = int(movie_id)
        return movie_id in data.get(str(user_id), [])