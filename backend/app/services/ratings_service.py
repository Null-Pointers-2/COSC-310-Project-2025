"""Ratings service."""
from typing import List, Optional
from datetime import datetime, timezone
from app.repositories.ratings_repo import RatingsRepository
from app.repositories.recommendations_repo import RecommendationsRepository
from app.schemas.rating import Rating, RatingCreate, RatingUpdate
import uuid

ratings_repo = RatingsRepository()
recommendations_repo = RecommendationsRepository()

def create_rating(user_id: str, rating_data: RatingCreate) -> Rating:
    """Create a new rating."""
    # DONE: Check if user already rated this movie
    # If yes, update existing; if no, create new
    # Clear user's cached recommendations
    
    existing = ratings_repo.get_by_user_and_movie(user_id, rating_data.movie_id)

    if existing:
        existing["rating"] = rating_data.rating
        updated = ratings_repo.update(existing["id"], existing)
        # Clear Cahce
        recommendations_repo.clear_cache(user_id)
        return Rating(**updated)

    new_rating = ratings_repo.create({
        "user_id": user_id,
        "movie_id": rating_data.movie_id,
        "rating": rating_data.rating,
    })

    recommendations_repo.clear_cache(user_id)
    return Rating(**new_rating)
    
def get_user_ratings(user_id: str) -> List[Rating]:
    """Get all ratings by a user."""
    # DONE: Use ratings_repo.get_by_user()
    
    return ratings_repo.get_by_user(user_id)

def get_rating_by_id(rating_id: str) -> Optional[Rating]:
    """Get rating by ID."""
    # DONE: Use ratings_repo.get_by_id()
    
    return ratings_repo.get_by_id(rating_id)

def update_rating(rating_id: str, user_id: str, update_data: RatingUpdate) -> Optional[Rating]:
    """Update a rating."""
    # DONE: Verify user owns this rating
    # Update rating, clear cached recommendations
    
    existing = ratings_repo.get_by_id(rating_id)
    if not existing:
        return None
    if existing.user_id != user_id:
        # Users can only modify their own rating
        return None
    
    if update_data.rating is not None:
        existing.rating = update_data.rating
        existing.timestamp = datetime.now(timezone.utc)

    updated = ratings_repo.update(rating_id, existing)
    recommendations_repo.clear_cache(user_id)
    return updated

def delete_rating(rating_id: str, user_id: str, is_admin: bool = False) -> bool:
    """Delete a rating."""
    # DONE: Verify user owns rating or is admin
    # Delete and clear cached recommendations
    
    rating = ratings_repo.get_by_id(rating_id)
    if not rating:
        return False
    
    # User must own the rating or have admin privledges
    if rating["user_id"] != user_id and not is_admin:
        return False

    ratings_repo.delete(rating_id)
    recommendations_repo.clear_cache(user_id)
    return True

def get_user_rating_stats(user_id: str) -> dict:
    """Get user's rating statistics."""
    # TODO: Calculate total ratings, average, favorite genre, etc.
    
    ratings = ratings_repo.get_by_user(user_id)
    if not ratings:
        return {"total_ratings": 0, "average_rating": 0, "favorite_genre": None}
    
    avg = round(sum(r.rating for r in ratings) / len(ratings))

    # Try to calculate favorite genre if a user rated any movie with a genre
    try:
        from app.repositories.movies_repo import MoviesRepository
        movies_repo = MoviesRepository()
        genres = []
        for r in ratings:
            movie = movies_repo.get_by_id(r.movie_id)
            if movie and "genre" in movie:
                genres.extend(movie["genre"].split(","))
        favorite_genre = max(set(genres), key=genres.count) if genres else None
    except Exception:
        favorite_genre = None

    return{
        "total_ratings": len(ratings),
        "average_rating": avg,
        "favorite_genre": favorite_genre,
    }