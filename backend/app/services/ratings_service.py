"""Ratings service."""

from app.schemas.rating import Rating, RatingCreate, RatingUpdate


def create_rating(resources, user_id: str, rating_data: RatingCreate) -> Rating:
    """Create a new rating."""
    existing = resources.ratings_repo.get_by_user_and_movie(user_id, rating_data.movie_id)

    if existing:
        raise ValueError(f"Rating already exists for movie {rating_data.movie_id}")

    new_rating = resources.ratings_repo.create(
        {
            "user_id": user_id,
            "movie_id": rating_data.movie_id,
            "rating": rating_data.rating,
        },
    )

    return Rating(**new_rating)


def get_user_ratings(resources, user_id: str) -> list[Rating]:
    """Get all ratings by a user."""
    ratings = resources.ratings_repo.get_by_user(user_id)
    return [Rating(**r) for r in ratings]


def get_rating_by_id(resources, rating_id: int) -> Rating | None:
    """Get rating by ID."""
    rating = resources.ratings_repo.get_by_id(rating_id)
    if rating:
        return Rating(**rating)
    return None


def update_rating(resources, rating_id: int, user_id: str, update_data: RatingUpdate) -> Rating | None:
    """Update an existing rating."""
    existing = resources.ratings_repo.get_by_id(rating_id)
    if not existing:
        return None
    if existing["user_id"] != user_id:
        return None

    update_dict = {}
    if update_data.rating is not None:
        update_dict["rating"] = update_data.rating

    updated = resources.ratings_repo.update(rating_id, update_dict)
    if updated:
        return Rating(**updated)
    return None


def delete_rating(resources, rating_id: int, user_id: str, *, is_admin: bool = False) -> bool:
    """Delete a rating."""
    rating = resources.ratings_repo.get_by_id(rating_id)
    if not rating:
        return False

    if not is_admin and rating["user_id"] != user_id:
        return False

    resources.ratings_repo.delete(rating_id)

    return True
