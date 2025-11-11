"""Admin endpoints."""
from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from app.schemas.user import User
from app.schemas.penalty import Penalty, PenaltyCreate
from app.core.dependencies import get_current_admin_user, get_resources
from app.services import admin_service

router = APIRouter()

@router.get("/users")
def get_all_users(current_admin: dict = Depends(get_current_admin_user), resources=Depends(get_resources)):
    """Get all users with statistics."""
    return admin_service.get_all_users_with_stats(resources)

@router.post("/penalties", response_model=Penalty, status_code=status.HTTP_201_CREATED)
def apply_penalty(penalty_data: PenaltyCreate, current_admin: dict = Depends(get_current_admin_user), resources=Depends(get_resources)):
    """Apply a penalty to a user."""
    admin_id = current_admin["id"]
    return admin_service.apply_penalty(resources, admin_id, penalty_data)

@router.get("/penalties", response_model=List[Penalty])
def get_all_penalties(current_admin: dict = Depends(get_current_admin_user), resources=Depends(get_resources)):
    """Get all penalties."""
    return admin_service.get_all_penalties(resources)

@router.get("/penalties/user/{user_id}", response_model=List[Penalty])
def get_user_penalties(
    user_id: str,
    current_admin: dict = Depends(get_current_admin_user),
    resources=Depends(get_resources)
):
    """Get penalties for a specific user."""
    return admin_service.get_user_penalties(resources, user_id)

@router.put("/penalties/{penalty_id}/resolve")
def resolve_penalty(penalty_id: str, current_admin: dict = Depends(get_current_admin_user), resources=Depends(get_resources)):
    """Mark a penalty as resolved."""
    success = admin_service.resolve_penalty(resources, penalty_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Penalty {penalty_id} not found"
        )
    return {"message": "Penalty resolved successfully"}

@router.delete("/penalties/{penalty_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_penalty(penalty_id: str, current_admin: dict = Depends(get_current_admin_user), resources=Depends(get_resources)):
    """Delete a penalty."""
    success = admin_service.delete_penalty(resources, penalty_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Penalty {penalty_id} not found"
        )
    return None

@router.get("/stats")
def get_system_stats(current_admin: dict = Depends(get_current_admin_user), resources=Depends(get_resources)):
    """Get system-wide statistics."""
    return admin_service.get_system_stats(resources)

@router.get("/violations/{user_id}")
def check_user_violations(user_id: str, current_admin: dict = Depends(get_current_admin_user), resources=Depends(get_resources)):
    """Check for user violations."""
    violations = admin_service.check_user_violations(resources, user_id)
    return {"user_id": user_id, "violations": violations}