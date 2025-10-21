"""User management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.user import User, UserProfile, UserDashboard, UserUpdate
from app.core.dependencies import get_current_user, get_current_admin_user
from app.services import users_service

router = APIRouter()

@router.get("/me", response_model=UserProfile)
def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's profile."""
    # TODO: Call users_service.get_user_profile()
    pass

@router.get("/me/dashboard", response_model=UserDashboard)
def get_my_dashboard(current_user: dict = Depends(get_current_user)):
    """Get current user's dashboard."""
    # TODO: Call users_service.get_user_dashboard()
    pass

@router.put("/me", response_model=User)
def update_my_profile(
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update current user's profile."""
    # TODO: Call users_service.update_user()
    pass

@router.get("", response_model=List[User])
def get_all_users(current_user: dict = Depends(get_current_admin_user)):
    """Get all users (admin only)."""
    # TODO: Call users_service.get_all_users()
    pass

@router.get("/{user_id}", response_model=UserProfile)
def get_user_profile(
    user_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """Get specific user's profile (admin only)."""
    # TODO: Call users_service.get_user_profile()
    pass
