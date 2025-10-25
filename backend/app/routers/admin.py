"""Admin endpoints."""
from fastapi import APIRouter, Depends, status
from typing import List
from app.schemas.user import User
from app.schemas.penalty import Penalty, PenaltyCreate
from app.core.dependencies import get_current_admin_user
from app.services import admin_service

router = APIRouter()

@router.get("/users", response_model=List[User])
def get_all_users(current_admin: dict = Depends(get_current_admin_user)):
    """Get all users with statistics."""
    # TODO: Call admin_service.get_all_users_with_stats()
    pass

@router.post("/penalties", response_model=Penalty, status_code=status.HTTP_201_CREATED)
def apply_penalty(penalty_data: PenaltyCreate, current_admin: dict = Depends(get_current_admin_user)):
    """Apply a penalty to a user."""
    # TODO: Call admin_service.apply_penalty()
    pass

@router.get("/penalties", response_model=List[Penalty])
def get_all_penalties(current_admin: dict = Depends(get_current_admin_user)):
    """Get all penalties."""
    # TODO: Call admin_service.get_all_penalties()
    pass

@router.get("/penalties/user/{user_id}", response_model=List[Penalty])
def get_user_penalties(
    user_id: str,
    current_admin: dict = Depends(get_current_admin_user)
):
    """Get penalties for a specific user."""
    # TODO: Call admin_service.get_user_penalties()
    pass

@router.put("/penalties/{penalty_id}/resolve")
def resolve_penalty(penalty_id: str, current_admin: dict = Depends(get_current_admin_user)):
    """Mark a penalty as resolved."""
    # TODO: Call admin_service.resolve_penalty()
    pass

@router.delete("/penalties/{penalty_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_penalty(penalty_id: str, current_admin: dict = Depends(get_current_admin_user)):
    """Delete a penalty."""
    # TODO: Call admin_service.delete_penalty()
    pass

@router.get("/stats")
def get_system_stats(current_admin: dict = Depends(get_current_admin_user)):
    """Get system-wide statistics."""
    # TODO: Call admin_service.get_system_stats()
    pass

@router.get("/violations/{user_id}")
def check_user_violations(user_id: str, current_admin: dict = Depends(get_current_admin_user)):
    """Check for user violations."""
    # TODO: Call admin_service.check_user_violations()
    pass