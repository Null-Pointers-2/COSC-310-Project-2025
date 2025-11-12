"""Authentication and authorization service."""

from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.dependencies import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str, password_hasher: PasswordHasher) -> bool:
    """Verify a password against its hash."""
    try:
        password_hasher.verify(hashed_password, plain_password)

    except VerifyMismatchError:
        return False

    return True


def get_password_hash(password: str, password_hasher: PasswordHasher) -> str:
    """Hash a password."""
    return password_hasher.hash(password)


def authenticate_user(username: str, password: str, resources):
    """Authenticate a user by username and password."""
    user = resources.users_repo.get_by_username(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"], resources.password_hasher):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta if expires_delta else datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_user_from_token(token: str, resources) -> dict | None:
    """Get user information from a JWT token."""
    try:
        token_data = decode_token(token, resources.users_repo)
        user = resources.users_repo.get_by_username(token_data["username"])
        if not user:
            return None

    except HTTPException:
        return None

    return user


def register_user(username: str, email: str, password: str, resources, role: str = "user") -> dict:
    """Register a new user."""
    existing_user = resources.users_repo.get_by_username(username)
    if existing_user:
        raise ValueError("Username already registered")

    existing_email = resources.users_repo.get_by_email(email)
    if existing_email:
        raise ValueError("Email already registered")

    hashed_password = get_password_hash(password, resources.password_hasher)

    user_data = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "role": role,
        "created_at": datetime.now(UTC).isoformat(),
    }
    return resources.users_repo.create(user_data)
