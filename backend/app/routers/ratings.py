"""Rating endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.rating import Rating, RatingCreate, RatingUpdate
from app.core.dependencies import get_current_user, get_current_admin_user
from app.services import ratings_service

router = APIRouter(preifx="/ratings", tags=["Ratings"])

@router.post("", response_model=Rating, status_code=status.HTTP_201_CREATED)
def create_rating(
    rating_data: RatingCreate,
    current_user: dict = Depends(get_current_user)
):
    """Rate a movie."""
    # DONE: Call ratings_service.create_rating()
    # Users can only modify their own ratings
    
    rating_data.user_id = current_user["id"]
    new_rating = ratings_service.create_rating(rating_data)
    if not new_rating:
        raise HTTPException(status_code=400, detail="Failed to create rating")
    return new_rating

@router.get("/me", response_model=List[Rating])
def get_my_ratings(current_user: dict = Depends(get_current_user)):
    """Get current user's ratings."""
    # DONE: Call ratings_service.get_user_ratings()
    
    ratings = ratings_service.get_user_ratings(current_user["id"])
    return ratings

@router.get("/{rating_id}", response_model=Rating)
def get_rating(
    rating_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific rating."""
    # DONE: Call ratings_service.get_rating_by_id()
    # Assuming users can see any rating

    rating = ratings_service.get_rating_by_id(rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    

@router.put("/{rating_id}", response_model=Rating)
def update_rating(
    rating_id: str,
    update_data: RatingUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a rating."""
    # TODO: Call ratings_service.update_rating()
    # Verify user owns this rating

    existing_rating = ratings_service.get_rating_by_id(rating_id)
    if not existing_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    if existing_rating.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Rating access restricted")
    
    updated = ratings_service.get_rating_by_id(rating_id, update_data)
    return updated

@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    rating_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a rating."""
    # DONE: Call ratings_service.delete_rating()
    # Verify user owns this rating
    
    rating = ratings_service.get_rating_by_id(rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    if rating.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Rating access restricted")

    ratings_service.delete_rating(rating_id)