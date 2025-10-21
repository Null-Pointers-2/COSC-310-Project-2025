"""Watchlist endpoints."""
from fastapi import APIRouter, Depends, status
from typing import List
from app.schemas.watchlist import WatchlistItem, WatchlistItemCreate
from app.core.dependencies import get_current_user
from app.services import watchlist_service

router = APIRouter(prefix="/watchlist")

@router.get("", response_model=List[WatchlistItem])
def get_my_watchlist(current_user: dict = Depends(get_current_user)):
    """Get current user's watchlist (Transaction 2)."""
    # TODO: Call watchlist_service.get_user_watchlist()
    pass

@router.post("", response_model=WatchlistItem, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    item: WatchlistItemCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add movie to watchlist."""
    # TODO: Call watchlist_service.add_to_watchlist()
    pass

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(
    movie_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove movie from watchlist."""
    # TODO: Call watchlist_service.remove_from_watchlist()
    pass

@router.get("/check/{movie_id}")
def check_in_watchlist(
    movie_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Check if movie is in watchlist."""
    # TODO: Call watchlist_service.is_in_watchlist()
    pass