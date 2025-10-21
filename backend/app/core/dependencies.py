"""
FastAPI dependencies for authentication and authorization.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.repositories.users_repo import UsersRepository
from app.repositories.penalties_repo import PenaltiesRepository

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

users_repo = UsersRepository()
penalties_repo = PenaltiesRepository()

def decode_token(token: str):
    """Decode and validate a JWT token."""
    # TODO: Decode JWT and return TokenData
    pass

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User dictionary
        
    Raises:
        HTTPException: If token is invalid or user not found
    """

    # TODO: Decode JWT token
    # TODO: Get user from repository
    pass


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to get current user and check if they have active penalties.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        User dictionary if no blocking penalties
        
    Raises:
        HTTPException: If user has blocking penalties
    """
    # TODO: Check for active penalties
    
    return current_user


async def get_current_admin_user(
    current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to verify current user has admin role.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        User dictionary if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    # TODO: Check if user has admin role
    
    return current_user


def check_rating_permission(user_id: str) -> bool:
    """
    Check if user has permission to create ratings.
    
    Args:
        user_id: User ID to check
        
    Returns:
        True if user can rate, False otherwise
    """
    # TODO: Check for active penalties that block rating
    pass


def check_export_permission(user_id: str) -> bool:
    """
    Check if user has permission to export data.
    
    Args:
        user_id: User ID to check
        
    Returns:
        True if user can export, False otherwise
    """
    # TODO: Check for active penalties that block exports
    pass
