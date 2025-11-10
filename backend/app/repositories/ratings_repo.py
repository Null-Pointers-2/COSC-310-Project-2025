"""Repository for ratings data operations."""
from typing import List, Optional, Dict
from pathlib import Path
from datetime import datetime, timezone
import json

class RatingsRepository:
    """Handle user ratings stored in JSON."""
    
    def __init__(self, ratings_file: str = "app/data/ratings.json"):
        """Initialize with path to ratings JSON file."""
        self.ratings_file = Path(ratings_file)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create ratings file if it doesn't exist."""
        if not self.ratings_file.exists():
            self.ratings_file.parent.mkdir(parents=True, exist_ok=True)
            self.ratings_file.write_text("[]", encoding="utf-8")
    
    def _read(self) -> List[Dict]:
        """Read all ratings from file."""
        try:
            with open(self.ratings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            self.ratings_file.write_text("[]", encoding="utf-8")
            return []
    
    def _write(self, ratings: List[Dict]):
        """Write all ratings to file."""
        with open(self.ratings_file, "w", encoding="utf-8") as f:
            json.dump(ratings, f, indent=2, ensure_ascii=False)
    
    def _get_next_id(self) -> int:
        """Get next available ID."""
        ratings = self._read()
        if not ratings:
            return 1
        return max(r["id"] for r in ratings) + 1

    def get_all(self) -> List[Dict]:
        """Get all ratings."""
        return self._read()
    
    def get_by_id(self, rating_id: int) -> Optional[Dict]:
        """Get rating by ID."""
        ratings = self._read()
        return next((r for r in ratings if r["id"] == rating_id), None)
    
    def get_by_user(self, user_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get all ratings by a user, optionally limited to most recent N ratings."""
        ratings = self._read()
        user_ratings = [r for r in ratings if r["user_id"] == user_id]
        
        # Sort by timestamp descending
        user_ratings.sort(key=lambda r: r["timestamp"], reverse=True)
        
        if limit is not None:
            return user_ratings[:limit]
        return user_ratings
    
    def get_by_movie(self, movie_id: int) -> List[Dict]:
        """Get all ratings for a movie."""
        ratings = self._read()
        return [r for r in ratings if r["movie_id"] == movie_id]
    
    def get_by_user_and_movie(self, user_id: str, movie_id: int) -> Optional[Dict]:
        """Get a specific user's rating for a movie."""
        ratings = self._read()
        return next(
            (r for r in ratings if r["user_id"] == user_id and r["movie_id"] == movie_id),
            None,
        )
    
    def create(self, rating_data: Dict) -> Dict:
        """Create a new rating."""
        ratings = self._read()
        new_rating = {
            "id": self._get_next_id(),
            "user_id": rating_data["user_id"],
            "movie_id": int(rating_data["movie_id"]),
            "rating": rating_data["rating"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        ratings.append(new_rating)
        self._write(ratings)
        return new_rating
    
    def update(self, rating_id: int, rating_data: Dict) -> Optional[Dict]:
        """Update an existing rating."""
        ratings = self._read()
        for i, r in enumerate(ratings):
            if r["id"] == rating_id:
                updated = {**r, **rating_data, "timestamp": datetime.now(timezone.utc).isoformat()}
                ratings[i] = updated
                self._write(ratings)
                return updated
        return None
    
    def delete(self, rating_id: int) -> bool:
        """Delete a rating."""
        ratings = self._read()
        new_ratings = [r for r in ratings if r["id"] != rating_id]
        if len(new_ratings) == len(ratings):
            return False
        self._write(new_ratings)
        return True