"""Recommendation endpoints."""
from fastapi import APIRouter, Depends, Query
from typing import List
from app.schemas.recommendation import RecommendationList, RecommendationItem
from app.schemas.movie import Movie
from app.core.dependencies import get_current_user, get_resources
from app.services import recommendations_service

router = APIRouter()

@router.get("/me", response_model=RecommendationList)
def get_my_recommendations(
    limit: int = Query(10, ge=1, le=50),
    force_refresh: bool = Query(False, description="Force regenerate recommendations"),
    current_user: dict = Depends(get_current_user),
    resources=Depends(get_resources)
):
    """Get personalized recommendations (Transaction 3)."""
    return recommendations_service.get_recommendations(
        resources, 
        user_id=current_user["id"], 
        limit=limit, 
        force_refresh=force_refresh
    )

@router.post("/me/refresh", response_model=RecommendationList)
def refresh_my_recommendations(
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
    resources=Depends(get_resources)
):
    """Force refresh recommendations."""
    return recommendations_service.refresh_recommendations_for_user(
        resources,
        user_id=current_user["id"],
        limit=limit
    )

@router.get("/similar/{movie_id}", response_model=List[RecommendationItem])
def get_similar_movies(
    movie_id: int,
    limit: int = Query(10, ge=1, le=50),
    resources=Depends(get_resources)
):
    """Get movies similar to a specific movie."""
    return recommendations_service.get_similar_movies(
        resources,
        movie_id=movie_id,
        limit=limit
    )