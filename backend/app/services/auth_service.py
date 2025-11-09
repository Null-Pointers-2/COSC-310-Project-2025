"""Authentication and authorization service."""
from app.repositories.users_repo import UsersRepository
from typing import Optional
from app.core.dependencies import decode_token
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from app.core.config import settings

users_repo = UsersRepository()
password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return password_hash.hash(password)

def authenticate_user(username: str, password: str):
    """Authenticate a user by username and password."""
    user = users_repo.get_by_username(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_user_from_token(token: str) -> Optional[dict]:
    """Get user information from a JWT token."""
    try:
        token_data = decode_token(token)
        user = users_repo.get_by_username(token_data["username"])
        if not user:
            return None
        return user
    except HTTPException:
        return None

def register_user(username: str, email: str, password: str, role: str = "user") -> dict:
    """Register a new user."""
    existing_user = users_repo.get_by_username(username)
    if existing_user:
        raise ValueError("Username already registered")

    existing_email = users_repo.get_by_email(email)
    if existing_email:
        raise ValueError("Email already registered")
    
    hashed_password = get_password_hash(password)

    user_data = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "role": role,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    new_user = users_repo.create(user_data)
    return new_user