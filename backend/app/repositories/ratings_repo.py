"""Repository for ratings data operations."""
from typing import List, Optional, Dict
from pathlib import Path
from datetime import datetime, timezone
import json
import uuid

class RatingsRepository:
    """Handle user ratings stored in JSON."""
    
    def __init__(self, ratings_file: str = "app/data/ratings.json"):
        """Initialize with path to ratings JSON file."""
        self.ratings_file = Path(ratings_file)
        self._ensure_file_exists()

    # Helper functions
    
    def _ensure_file_exists(self):
        """Create ratings file if it doesn't exist."""
        # DONE: Create empty JSON array if file doesn't exist
        
        if not self.ratings_file.exists():
            self.ratings_file.parent.mkdir(parents=True, exist_ok=True)
            self.ratings_file.write_text("[]", encoding="utf-8")
    
    def _read(self) -> List[Dict]:
        """Read all ratings from file."""
        # DONE: Load JSON from file
        try:
            with open(self.ratings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If the file cannot be read reset it
            self.ratings_file.write_text("[]", encoding="utf-8")
            return []
    
    def _write(self, ratings: List[Dict]):
        """Write all ratings to file."""
        # DONE: Save JSON to file
        with open(self.ratings_file, "w", encoding="utf-8") as f:
            json.dump(ratings, f, indent=2, ensure_ascii=False)
        
    # Create, update, read, and write functions related to API

    def get_all(self) -> List[Dict]:
        """Get all ratings."""
        # DONE: Implement
        return self._read()
    
    def get_by_id(self, rating_id: str) -> Optional[Dict]:
        """Get rating by ID."""
        # DONE: Implement
        ratings =self._read()
        return next((r for r in ratings if r["id"] == rating_id), None)
    
    def get_by_user(self, user_id: str) -> List[Dict]:
        """Get all ratings by a user."""
        # DONE: Filter by user_id
        ratings = self._read()
        return [r for r in ratings if r["user_id"] == user_id]
    
    def get_by_movie(self, movie_id: str) -> List[Dict]:
        """Get all ratings for a movie."""
        # DONE: Filter by movie_id
        ratings = self._read()
        return [r for r in ratings if r["movie_id"] == movie_id]
    
    def get_by_user_and_movie(self, user_id: str, movie_id: str) -> Optional[Dict]:
        """Get a specific user's rating for a movie."""
        # DONE: Find rating by user_id and movie_id
        ratings = self._read()
        return next(
            (r for r in ratings if r["user_id"] == user_id and str(r["movie_id"]) == str(movie_id)),
            None,
        )
    
    def create(self, rating_data: Dict) -> Dict:
        """Create a new rating."""
        # DONE: Add to ratings list and save
        # Generate ID, add timestamp
        ratings = self._read()
        new_rating = {
            "id": str(uuid.uuid4()),
            "user_id": rating_data["user_id"],
            "movie_id": rating_data["movie_id"],
            "rating": rating_data["rating"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        ratings.append(new_rating)
        self._write(ratings)
        return new_rating
    
    def update(self, rating_id: str, rating_data: Dict) -> Optional[Dict]:
        """Update an existing rating."""
        # DONE: Find and update rating
        ratings = self._read()
        for i, r in enumerate(ratings):
            if r["id"] == rating_id:
                # Add updates to the original rating
                updated = {**r, **rating_data, "timestamp": datetime.now(timezone.utc).isoformat()}
                ratings[i] = updated
                self._write(ratings)
                return updated
        return None
    
    def delete(self, rating_id: str) -> bool:
        """Delete a rating."""
        # DONE: Remove from list and save
        ratings = self._read()
        new_ratings = [r for r in ratings if r["id"] != rating_id]
        if len(new_ratings) == len(ratings):
            # Rating does not exists or not found
            return False
        self._write(new_ratings)
        return True