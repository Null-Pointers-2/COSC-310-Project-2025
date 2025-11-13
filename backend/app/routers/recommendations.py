"""Recommendation endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_user, get_resources
from app.main import SingletonResources
from app.schemas.recommendation import RecommendationItem, RecommendationList
from app.services import recommendations_service

router = APIRouter()


@router.get("/me", response_model=RecommendationList)
def get_my_recommendations(
    current_user: Annotated[dict, Depends(get_current_user)],
    resources: Annotated[SingletonResources, Depends(get_resources)],
    *,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    force_refresh: Annotated[bool, Query(description="Force regenerate recommendations")] = False,
):
    """Get personalized recommendations."""
    return recommendations_service.get_recommendations(
        resources,
        user_id=current_user["id"],
        limit=limit,
        force_refresh=force_refresh,
    )


@router.post("/me/refresh", response_model=RecommendationList)
def refresh_my_recommendations(
    current_user: Annotated[dict, Depends(get_current_user)],
    resources: Annotated[SingletonResources, Depends(get_resources)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
):
    """Force refresh recommendations."""
    return recommendations_service.refresh_recommendations_for_user(resources, user_id=current_user["id"], limit=limit)


@router.get("/similar/{movie_id}", response_model=list[RecommendationItem])
def get_similar_movies(
    resources: Annotated[SingletonResources, Depends(get_resources)],
    movie_id: int,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
):
    """Get movies similar to a specific movie."""
    return recommendations_service.get_similar_movies(resources, movie_id=movie_id, limit=limit)
