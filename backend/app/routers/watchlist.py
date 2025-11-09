"""Watchlist endpoints."""
from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from app.schemas.watchlist import WatchlistItem, WatchlistItemCreate
from app.core.dependencies import get_current_user
from app.services import watchlist_service

router = APIRouter(prefix="/watchlist")

@router.get("", response_model=List[WatchlistItem])
def get_my_watchlist(current_user: dict = Depends(get_current_user)):
    """Get current user's watchlist."""
    watchlist = watchlist_service.get_user_watchlist(user_id = current_user["id"])
    if watchlist is None:
        raise HTTPException(status_code=404, detail=f"Watchlist with ID {current_user['id']} not found")
    return watchlist
    

@router.post("", response_model=WatchlistItem, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(item: WatchlistItemCreate, current_user: dict = Depends(get_current_user)):
    """Add movie to watchlist."""
    try:
        return watchlist_service.add_to_watchlist(user_id = current_user["id"], item = item)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
    

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(movie_id: str, current_user: dict = Depends(get_current_user)):
    """Remove movie from watchlist."""
    try:
        return watchlist_service.remove_from_watchlist(user_id = current_user["id"], movie_id = movie_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.get("/check/{movie_id}")
def check_in_watchlist(movie_id: str, current_user: dict = Depends(get_current_user)):
    """Check if movie is in watchlist."""
    try:
        return watchlist_service.is_in_watchlist(user_id = current_user["id"], movie_id = movie_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    