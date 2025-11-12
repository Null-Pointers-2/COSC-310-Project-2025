"""Rating endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_active_user, get_resources
from app.schemas.rating import Rating, RatingCreate, RatingUpdate
from app.services import ratings_service


router = APIRouter()


@router.post("", response_model=Rating, status_code=status.HTTP_201_CREATED)
def create_rating(
    rating_data: RatingCreate,
    current_user: dict = Depends(get_current_active_user),
    resources=Depends(get_resources),
):
    """Rate a movie."""
    try:
        return ratings_service.create_rating(resources, current_user["id"], rating_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/me", response_model=list[Rating])
def get_my_ratings(
    current_user: dict = Depends(get_current_active_user),
    resources=Depends(get_resources),
):
    """Get current user's ratings."""
    return ratings_service.get_user_ratings(resources, current_user["id"])


@router.get("/{rating_id}", response_model=Rating)
def get_rating(
    rating_id: int,
    resources=Depends(get_resources),
):
    """Get specific rating."""
    rating = ratings_service.get_rating_by_id(resources, rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating


@router.put("/{rating_id}", response_model=Rating)
def update_rating(
    rating_id: int,
    update_data: RatingUpdate,
    current_user: dict = Depends(get_current_active_user),
    resources=Depends(get_resources),
):
    """Update a rating."""
    existing_rating = ratings_service.get_rating_by_id(resources, rating_id)
    if not existing_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    if existing_rating.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Rating access restricted")

    updated = ratings_service.update_rating(resources, rating_id, current_user["id"], update_data)
    if not updated:
        raise HTTPException(status_code=400, detail="Failed to update rating")
    return updated


@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    rating_id: int,
    current_user: dict = Depends(get_current_active_user),
    resources=Depends(get_resources),
):
    """Delete a rating."""
    rating = ratings_service.get_rating_by_id(resources, rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    if rating.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Rating access restricted")

    success = ratings_service.delete_rating(resources, rating_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete rating")
