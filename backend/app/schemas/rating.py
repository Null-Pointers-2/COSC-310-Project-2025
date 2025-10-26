"""Rating schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RatingBase(BaseModel):
    """Base rating schema."""
    movie_id: str = Field(..., description="Movie ID")
    rating: float = Field(..., ge=0.5, le=5.0, description="Rating from 0.5 to 5.0")

class RatingCreate(RatingBase):
    """Schema for creating a new rating."""
    user_id: str = Field(..., description="User ID who created the rating")

class RatingUpdate(BaseModel):
    """Schema for updating a rating."""
    rating: Optional[float] = Field(None, ge=0.5, le=5.0)

class Rating(RatingBase):
    """Complete rating schema."""
    id: str
    user_id: str
    timestamp: datetime
    
    class Config:
        from_attributes = True