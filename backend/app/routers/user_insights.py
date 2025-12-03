"""User insights endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user, get_resources
from app.core.resources import SingletonResources
from app.schemas.user_insights import UserInsights, UserInsightsSummary
from app.services import user_insights_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/me", response_model=UserInsights)
def get_my_insights(
    *,
    current_user: Annotated[dict, Depends(get_current_user)],
    resources: Annotated[SingletonResources, Depends(get_resources)],
):
    """
    Get comprehensive insights for the current user.

    Includes:
    - Favorite genres based on watchlist ratings
    - Favorite themes from genome tag analysis
    - Watchlist completion metrics

    Fresh insights are generated on every request.
    """
    logger.info("[INSIGHTS] Starting insights generation for user %s", current_user["id"])

    insights = user_insights_service.generate_user_insights(resources, user_id=current_user["id"])

    logger.info("[INSIGHTS] Insights generated: %s", insights is not None)

    if not insights:
        raise HTTPException(status_code=404, detail="Could not generate insights")

    logger.info("[INSIGHTS] Returning insights")
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
