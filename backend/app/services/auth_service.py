"""Authentication and authorization service."""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from app.repositories.users_repo import UsersRepository
from app.schemas.auth import TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
users_repo = UsersRepository()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    # TODO: Use pwd_context.verify()
    pass

def get_password_hash(password: str) -> str:
    """Hash a password."""
    # TODO: Use pwd_context.hash()
    pass

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate a user by username and password."""
    # TODO: Get user from repo, verify password
    pass

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    # TODO: Create JWT with expiration
    pass

def decode_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT token."""
    # TODO: Decode JWT and return TokenData
    pass

def register_user(username: str, email: str, password: str, role: str = "user") -> dict:
    """Register a new user."""
    # TODO: Hash password, create user in repo
    pass