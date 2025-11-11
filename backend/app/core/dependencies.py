"""
FastAPI dependencies for authentication and authorization.
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_resources(request: Request):
    """Get singleton resources from app state."""
    return request.app.state.resources

def decode_token(token: str, users_repo) -> dict:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string
        users_repo: Users repository instance

    Returns:
        Dictionary with user_id, username, and role

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = users_repo.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "user_id": user["id"],
            "username": username,
            "role": user["role"]
        }
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    resources = Depends(get_resources)
) -> dict:
    """
    Dependency to get the current authenticated user from JWT token.

    Args:
        token: JWT token from Authorization header
        resources: Singleton resources from app state

    Returns:
        User dictionary

    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        token_data = decode_token(token, resources.users_repo)
        user = resources.users_repo.get_by_username(token_data["username"])

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
    resources = Depends(get_resources)
) -> dict:
    """
    Dependency to get current user and check if they have active penalties.

    Args:
        current_user: User from get_current_user dependency
        resources: Singleton resources from app state

    Returns:
        User dictionary if no blocking penalties

    Raises:
        HTTPException: If user has blocking penalties
    """
    active_penalties = resources.penalties_repo.get_active_by_user(current_user["id"])

    if active_penalties:
        penalty_reasons = [p["reason"] for p in active_penalties]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account has active penalties: {', '.join(penalty_reasons)}"
        )

    return current_user


async def get_current_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to verify current user has admin role.
    
    Args:
        current_user: User from get_current_user dependency
    
    Returns:
        User dictionary if admin
    
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user