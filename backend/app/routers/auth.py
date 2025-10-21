"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.auth import Token
from app.schemas.user import UserCreate, User
from app.services import auth_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate):
    """Register a new user."""
    # TODO: Implement registration
    # Check if username/email already exists
    # Call auth_service.register_user()
    pass

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token."""
    # TODO: Authenticate user
    # Call auth_service.authenticate_user()
    # Generate token with auth_service.create_access_token()
    pass

@router.get("/me", response_model=User)
def get_current_user_info(token: str = Depends(oauth2_scheme)):
    """Get current user information."""
    # TODO: Decode token, get user info
    pass