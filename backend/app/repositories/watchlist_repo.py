"""Repository for user watchlist operations."""
import json
from typing import List, Optional, Dict
from pathlib import Path
from datetime import datetime

class WatchlistRepository:
    """Handle user watchlists stored in JSON."""
    
    def __init__(self, watchlist_file: str = "app/data/watchlist.json"):
        """Initialize with path to watchlist JSON file."""
        self.watchlist_file = Path(watchlist_file)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create watchlist file if it doesn't exist."""
        if not self.watchlist_file.exists():

            # Ensure the parent directory exists
            self.watchlist_file.parent.mkdir(parents=True, exist_ok=True)

            # Create the watchlist and write an empty dict to it
            self.watchlist_file.write_text("{}")
            return False # False if the file did not exist
        return True # True if the file already existed
      
    
    def _read(self) -> Dict[str, List[str]]:
        """Read all watchlist items."""
        try:
            content = self.watchlist_file.read_text()
            return json.loads(content)
        except (IOError, json.JSONDecodeError):
            # if the file cannot be read or is invalid, return empty dict
            return {}
    
    def _write(self, data: Dict[str, List[str]]):
        """Write all watchlist items to file."""
        with self.watchlist_file.open("w") as f:
            json.dump(data, f, indent=4)    
       
            
    
    def get_by_user(self, user_id: str) -> List[Dict]:
        """Get user's watchlist."""
        data = self._read()
        return data.get(str(user_id), [])
    
    def add(self, user_id: str, movie_id: str) -> Dict:
        """Add movie to user's watchlist."""
        data = self._read()
        user_key = str(user_id)
        movie_id = str(movie_id)   

        if user_key not in data:
            data[user_key] = []
        
        if movie_id not in data[user_key]:
            data[user_key].append(movie_id)
            self._write(data)   
        
        return {"user_id": user_id, "movie_id": movie_id}
        
    
    def remove(self, user_id: str, movie_id: str) -> bool:
        """Remove movie from user's watchlist."""
        data = self._read()
        user_key = str(user_id)
        movie_id = str(movie_id)

        if user_key in data and movie_id in data[user_key]: # Check if the movie exists in the user's watchlist
            data[user_key].remove(movie_id)
            self._write(data)
            return True
        return False
    
    def exists(self, user_id: str, movie_id: str) -> bool:
        """Check if movie is in user's watchlist."""
        data = self._read()
        return movie_id in data.get(str(user_id), [])