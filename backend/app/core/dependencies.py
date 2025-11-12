"""
FastAPI dependencies for authentication and authorization.
"""

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_resources(request: Request):
    """Get singleton resources from app state."""
    return request.app.state.resources


def raise_auth_exception(detail: str = "Could not validate credentials"):
    """Raises the standard 401 Unauthorized exception."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def decode_token_payload(token: str) -> str | None:
    """
    Decodes and validates a JWT token and returns the username (sub).

    Raises:
        InvalidTokenError: If token is invalid or expired.
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    username: str = payload.get("sub")

    if not username:
        raise InvalidTokenError("Token payload missing required subject.")

    return username


async def get_current_user(token: str = Depends(oauth2_scheme), resources=Depends(get_resources)) -> dict:
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
        username = decode_token_payload(token)
        user = resources.users_repo.get_by_username(username)

    except InvalidTokenError:
        raise_auth_exception()

    else:
        if user is None:
            raise_auth_exception(detail="User not found")

    return {"user_id": user["id"], "username": username, "role": user["role"]}


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
    resources=Depends(get_resources),
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
            detail=f"Account has active penalties: {', '.join(penalty_reasons)}",
        )

    return current_user


async def get_current_admin_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user
