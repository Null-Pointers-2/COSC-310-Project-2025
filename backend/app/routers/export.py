"""Data export endpoints."""
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
import json
from io import BytesIO

from app.core.dependencies import get_current_user, get_resources
from app.core.resources import SingletonResources
from app.services import ratings_service, recommendations_service, users_service, watchlist_service

router = APIRouter()

def as_download(data: dict | list, filename: str):
    json_bytes = json.dumps(jsonable_encoder(data)).encode("utf-8")
    return StreamingResponse(
        BytesIO(json_bytes),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/profile")
def export_my_profile(current_user: Annotated[dict, Depends(get_current_user)],
                      resources: Annotated[SingletonResources, Depends(get_resources)]):
    '''Export user's profile as JSON'''
    user_id = current_user["id"]
    profile = users_service.get_user_profile(user_id, resources)

    return as_download(profile, f"user_{user_id}_profile.json")


@router.get("/ratings")
def export_my_ratings(current_user: Annotated[dict, Depends(get_current_user)],
                      resources: Annotated[SingletonResources, Depends(get_resources)]):
    """Export user's ratings as JSON."""
    user_id = current_user["id"]
    ratings = ratings_service.get_user_ratings(resources, user_id)

    return as_download(ratings, f"user_{user_id}_ratings.json")


@router.get("/watchlist")
def export_my_watchlist(current_user: Annotated[dict, Depends(get_current_user)],
                        resources: Annotated[SingletonResources, Depends(get_resources)]):
    """Export user's watchlist as JSON."""

    user_id = current_user["id"]
    watchlist = watchlist_service.get_user_watchlist(resources, user_id)

    return as_download(watchlist, f"user_{user_id}_watchlist.json")


@router.get("/recommendations")
def export_my_recommendations(current_user: Annotated[dict, Depends(get_current_user)],
                              resources: Annotated[SingletonResources, Depends(get_resources)]):
    """Export user's recommendations as JSON."""

    user_id = current_user["id"]
    recommendations = recommendations_service.get_recommendations(resources, user_id, 1000).model_dump()

    return as_download(recommendations, f"user_{user_id}_recommendations.json")


@router.get("/export_all")
def export_all_data(current_user: Annotated[dict, Depends(get_current_user)],
                    resources: Annotated[SingletonResources, Depends(get_resources)]):
    """Export all user data as JSON."""
    user_id = current_user["id"]

    user_profile = users_service.get_user_profile(user_id, resources)
    ratings = ratings_service.get_user_ratings(resources, user_id)
    watchlist = watchlist_service.get_user_watchlist(resources, user_id)
    recommendations = recommendations_service.get_recommendations(resources, user_id, 1000).model_dump()

    all_data = {
        "profile": user_profile,
        "ratings": ratings,
        "watchlist": watchlist,
        "recommendations": recommendations,
    }

    return as_download(all_data, f"user_{user_id}_full_export.json")