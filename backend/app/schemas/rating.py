"""Rating schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RatingBase(BaseModel):
    """Base rating schema."""

    movie_id: int = Field(..., description="Movie ID")
    rating: float = Field(..., ge=0.5, le=5.0, description="Rating from 0.5 to 5.0")


class RatingCreate(RatingBase):
    """Schema for creating a new rating (user_id comes from auth token)."""


class RatingUpdate(BaseModel):
    """Schema for updating a rating."""

    rating: float | None = Field(None, ge=0.5, le=5.0)


class Rating(RatingBase):
    """Complete rating schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    timestamp: datetime
