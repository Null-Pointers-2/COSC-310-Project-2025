"""Rating endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.rating import Rating, RatingCreate, RatingUpdate
from app.core.dependencies import get_current_active_user
from app.services import ratings_service

router = APIRouter()

@router.post("", response_model=Rating, status_code=status.HTTP_201_CREATED)
def create_rating(rating_data: RatingCreate, current_user: dict = Depends(get_current_active_user)):
    """Rate a movie."""
    try:
        new_rating = ratings_service.create_rating(current_user["id"], rating_data)
        return new_rating
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=List[Rating])
def get_my_ratings(current_user: dict = Depends(get_current_active_user)):
    """Get current user's ratings."""
    ratings = ratings_service.get_user_ratings(current_user["id"])
    return ratings

@router.get("/{rating_id}", response_model=Rating)
def get_rating(rating_id: int, current_user: dict = Depends(get_current_active_user)):
    """Get specific rating."""
    rating = ratings_service.get_rating_by_id(rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating

@router.put("/{rating_id}", response_model=Rating)
def update_rating(rating_id: int, update_data: RatingUpdate, current_user: dict = Depends(get_current_active_user)):
    """Update a rating."""
    existing_rating = ratings_service.get_rating_by_id(rating_id)
    if not existing_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    if existing_rating.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Rating access restricted")

    updated = ratings_service.update_rating(rating_id, current_user["id"], update_data)
    if not updated:
        raise HTTPException(status_code=400, detail="Failed to update rating")
    return updated

@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(rating_id: int, current_user: dict = Depends(get_current_active_user)):
    """Delete a rating."""
    rating = ratings_service.get_rating_by_id(rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    if rating.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Rating access restricted")

    success = ratings_service.delete_rating(rating_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete rating")