"""User management endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import (
    get_current_admin_user,
    get_current_user,
    get_resources,
)
from app.main import SingletonResources
from app.schemas.user import User, UserDashboard, UserProfile, UserUpdate
from app.services import users_service

router = APIRouter()


@router.get("/me", response_model=UserProfile)
def get_my_profile(
    current_user: Annotated[dict, Depends(get_current_user)],
    resources: Annotated[SingletonResources, Depends(get_resources)],
):
    """Get current user's profile."""
    user_id = current_user["id"]
    profile = users_service.get_user_profile(user_id=user_id, resources=resources)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return profile


@router.get("/me/dashboard", response_model=UserDashboard)
def get_my_dashboard(
    current_user: Annotated[dict, Depends(get_current_user)],
    resources: Annotated[SingletonResources, Depends(get_resources)],
):
    """Get current user's dashboard."""
    user_id = current_user["id"]
    dashboard = users_service.get_user_dashboard(user_id=user_id, resources=resources)
    if not dashboard:
        raise HTTPException(status_code=404, detail="User dashboard not found")
    return dashboard


@router.put("/me", response_model=User)
def update_my_profile(
    update_data: UserUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    resources: Annotated[SingletonResources, Depends(get_resources)],
):
    """Update current user's profile."""
    user_id = current_user["id"]
    updated_user = users_service.update_user(user_id=user_id, update_data=update_data, resources=resources)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found for update")
    return updated_user


@router.get("", response_model=list[User])
def get_all_users(
    resources: Annotated[SingletonResources, Depends(get_resources)],
    _current_admin: Annotated[dict, Depends(get_current_admin_user)],
):
    """Get all users (admin only)."""
    return users_service.get_all_users(resources)


@router.get("/{user_id}", response_model=UserProfile)
def get_user_profile(
    user_id: str,
    resources: Annotated[SingletonResources, Depends(get_resources)],
    _current_admin: Annotated[dict, Depends(get_current_admin_user)],
):
    """Get specific user's profile (admin only)."""
    profile = users_service.get_user_profile(user_id, resources)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return profile
