"""Global insights endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import get_resources
from app.core.resources import SingletonResources
from app.schemas.global_insights import GlobalGenreLeaderboard
from app.services import global_insights_service

router = APIRouter()


@router.get("/genre-leaderboard", response_model=GlobalGenreLeaderboard)
def get_genre_leaderboard(
    resources: Annotated[SingletonResources, Depends(get_resources)],
):
    """
    Get global genre popularity leaderboard.

    Returns statistics for all genres across all users, ranked by popularity score.
    The popularity score combines rating frequency and average rating.
    """
    return global_insights_service.get_global_genre_leaderboard(resources)
