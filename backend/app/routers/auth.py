"""Authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.core.dependencies import get_resources
from app.core.resources import SingletonResources
from app.schemas.auth import Token
from app.schemas.user import User, UserCreate
from app.services import auth_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    resources: Annotated[SingletonResources, Depends(get_resources)],
):
    """Register a new user."""
    try:
        return auth_service.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            resources=resources,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    resources: Annotated[SingletonResources, Depends(get_resources)],
):
    """Authenticate user and return JWT access token."""
    user = auth_service.authenticate_user(form_data.username, form_data.password, resources)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token({"sub": user["username"]})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=User)
def get_current_user_info(
    token: Annotated[str, Depends(oauth2_scheme)],
    resources: Annotated[SingletonResources, Depends(get_resources)],
):
    """Return currently logged-in user info from JWT token."""
    user = auth_service.get_user_from_token(token, resources)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user
