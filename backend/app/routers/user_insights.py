"""User insights endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import get_current_user, get_resources
from app.core.resources import SingletonResources
from app.schemas.user_insights import UserInsights, UserInsightsSummary
from app.services import user_insights_service

router = APIRouter()


@router.get("/me", response_model=UserInsights)
def get_my_insights(
    *,
    force_refresh: Annotated[bool, Query(description="Force regenerate insights")] = False,
    current_user: Annotated[dict, Depends(get_current_user)],
    resources: Annotated[SingletonResources, Depends(get_resources)],
):
    """
    Get comprehensive insights for the current user.

    Includes:
    - Favorite genres based on watchlist ratings
    - Favorite themes from genome tag analysis
    - Watchlist completion metrics

    Results are cached. Use force_refresh=true to regenerate.
    """
    insights = user_insights_service.generate_user_insights(
        resources, user_id=current_user["id"], force_refresh=force_refresh
    )

    if not insights:
        raise HTTPException(status_code=404, detail="Could not generate insights")

    return insights


@router.get("/me/summary", response_model=UserInsightsSummary)
def get_my_insights_summary(
    current_user: Annotated[dict, Depends(get_current_user)],
    resources: Annotated[SingletonResources, Depends(get_resources)],
):
    """
    Get simplified insights summary for the current user.

    Returns only the key highlights:
    - Top genre and top 3 genres
    - Top theme and top 5 themes
    - Watchlist completion rate
    - Total ratings
    """
    summary = user_insights_service.get_user_insights_summary(resources, user_id=current_user["id"])

    if not summary:
        raise HTTPException(status_code=404, detail="Could not generate insights summary")

    return summary
