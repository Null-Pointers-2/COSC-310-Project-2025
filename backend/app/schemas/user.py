"""User schemas for authentication and profiles."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    email: EmailStr | None = None


class User(UserBase):
    """Complete user schema (without password)."""

    id: str
    role: str  # "admin" or "user"
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfile(User):
    """Extended user profile with statistics."""

    total_ratings: int = 0
    average_rating: float | None = None
    active_penalties: int = 0


class UserDashboard(BaseModel):
    """User dashboard data."""

    user: UserProfile
    recent_ratings: list
    recommendations: list
    penalties: list
