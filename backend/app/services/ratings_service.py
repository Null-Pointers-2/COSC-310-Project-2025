"""Ratings service."""
from typing import List, Optional
from app.repositories.ratings_repo import RatingsRepository
from app.schemas.rating import Rating, RatingCreate, RatingUpdate

ratings_repo = RatingsRepository()

def create_rating(user_id: str, rating_data: RatingCreate) -> Rating:
    """Create a new rating."""
    existing = ratings_repo.get_by_user_and_movie(user_id, rating_data.movie_id)

    if existing:
        raise ValueError(f"Rating already exists for movie {rating_data.movie_id}")

    new_rating = ratings_repo.create({
        "user_id": user_id,
        "movie_id": rating_data.movie_id,
        "rating": rating_data.rating,
    })

    return Rating(**new_rating)
    
def get_user_ratings(user_id: str) -> List[Rating]:
    """Get all ratings by a user."""
    ratings = ratings_repo.get_by_user(user_id)
    return [Rating(**r) for r in ratings]

def get_rating_by_id(rating_id: int) -> Optional[Rating]:
    """Get rating by ID."""
    rating = ratings_repo.get_by_id(rating_id)
    if rating:
        return Rating(**rating)
    return None

def update_rating(rating_id: int, user_id: str, update_data: RatingUpdate) -> Optional[Rating]:
    """Update an existing rating."""
    existing = ratings_repo.get_by_id(rating_id)
    if not existing:
        return None
    if existing["user_id"] != user_id:
        return None
    
    update_dict = {}
    if update_data.rating is not None:
        update_dict["rating"] = update_data.rating

    updated = ratings_repo.update(rating_id, update_dict)
    if updated:
        return Rating(**updated)
    return None

def delete_rating(rating_id: int, user_id: str, is_admin: bool = False) -> bool:
    """Delete a rating."""
    rating = ratings_repo.get_by_id(rating_id)
    if not rating:
        return False
    
    if rating["user_id"] != user_id and not is_admin:
        return False
    
    return ratings_repo.delete(rating_id)