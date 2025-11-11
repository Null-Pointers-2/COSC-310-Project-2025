"""User management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.user import User, UserProfile, UserDashboard, UserUpdate
from app.core.dependencies import get_current_user, get_current_admin_user, get_resources
from app.services import users_service

router = APIRouter()

@router.get("/me", response_model=UserProfile)
def get_my_profile(current_user: dict = Depends(get_current_user), resources=Depends(get_resources)):
    """Get current user's profile."""
    user_id = current_user["id"]
    profile = users_service.get_user_profile(user_id=user_id, resources=resources)
    if not profile:
        raise HTTPException(
            status_code=404, detail="User profile not found"
        )
    return profile

@router.get("/me/dashboard", response_model=UserDashboard)
def get_my_dashboard(current_user: dict = Depends(get_current_user), resources=Depends(get_resources)):
    """Get current user's dashboard."""
    user_id = current_user["id"]
    dashboard = users_service.get_user_dashboard(user_id=user_id, resources=resources)
    if not dashboard:
        raise HTTPException(
            status_code=404, detail="User dashboard not found"
        )
    return dashboard

@router.put("/me", response_model=User)
def update_my_profile(
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
    resources=Depends(get_resources)
):
    """Update current user's profile."""
    user_id = current_user["id"]
    updated_user = users_service.update_user(
        user_id=user_id, update_data=update_data, resources=resources
    )
    if not updated_user:
        raise HTTPException(
            status_code=404, detail="User not found for update"
        )
    return updated_user

@router.get("", response_model=List[User])
def get_all_users(current_user: dict = Depends(get_current_admin_user), resources=Depends(get_resources)):
    """Get all users (admin only)."""
    users = users_service.get_all_users(resources)
    return users

@router.get("/{user_id}", response_model=UserProfile)
def get_user_profile(
    user_id: str,
    current_user: dict = Depends(get_current_admin_user),
    resources=Depends(get_resources)
):
    """Get specific user's profile (admin only)."""
    profile = users_service.get_user_profile(user_id, resources)
    if not profile:
        raise HTTPException(
            status_code=404, detail="User profile not found"
        )
    return profile
