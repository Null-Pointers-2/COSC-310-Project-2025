"""Watchlist endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user, get_resources
from app.main import SingletonResources
from app.schemas.watchlist import WatchlistItem, WatchlistItemCreate
from app.services import watchlist_service

router = APIRouter(prefix="/watchlist")


@router.get("", response_model=list[WatchlistItem])
def get_my_watchlist(
    current_user: Annotated[dict, Depends(get_current_user)],
    resources: Annotated[SingletonResources, Depends(get_resources)],
):
    """Get current user's watchlist."""
    watchlist = watchlist_service.get_user_watchlist(resources, user_id=current_user["id"])
    if watchlist is None:
        raise HTTPException(status_code=404, detail=f"Watchlist with ID {current_user['id']} not found")
    return watchlist


@router.post("", response_model=WatchlistItem, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    item: WatchlistItemCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    resources: Annotated[SingletonResources, Depends(get_resources)],
):
    """Add movie to watchlist."""
    try:
        return watchlist_service.add_to_watchlist(resources, user_id=current_user["id"], item=item)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(
    movie_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    resources: Annotated[SingletonResources, Depends(get_resources)],
):
    """Remove movie from watchlist."""
    try:
        return watchlist_service.remove_from_watchlist(resources, user_id=current_user["id"], movie_id=movie_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/check/{movie_id}")
def check_in_watchlist(
    movie_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    resources: Annotated[dict, Depends(get_resources)],
):
    """Check if movie is in watchlist."""
    try:
        return watchlist_service.is_in_watchlist(resources, user_id=current_user["id"], movie_id=movie_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
