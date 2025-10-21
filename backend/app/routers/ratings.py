"""Rating endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.rating import Rating, RatingCreate, RatingUpdate
from app.core.dependencies import get_current_user, get_current_admin_user
from app.services import ratings_service

router = APIRouter()

@router.post("", response_model=Rating, status_code=status.HTTP_201_CREATED)
def create_rating(
    rating_data: RatingCreate,
    current_user: dict = Depends(get_current_user)
):
    """Rate a movie."""
    # TODO: Call ratings_service.create_rating()
    pass

@router.get("/me", response_model=List[Rating])
def get_my_ratings(current_user: dict = Depends(get_current_user)):
    """Get current user's ratings."""
    # TODO: Call ratings_service.get_user_ratings()
    pass

@router.get("/{rating_id}", response_model=Rating)
def get_rating(
    rating_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific rating."""
    # TODO: Call ratings_service.get_rating_by_id()
    pass

@router.put("/{rating_id}", response_model=Rating)
def update_rating(
    rating_id: str,
    update_data: RatingUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a rating."""
    # TODO: Call ratings_service.update_rating()
    # Verify user owns this rating
    pass

@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    rating_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a rating."""
    # TODO: Call ratings_service.delete_rating()
    # Verify user owns this rating
    pass
