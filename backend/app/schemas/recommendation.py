"""Recommendation schemas."""
from pydantic import BaseModel
from typing import List

class RecommendationItem(BaseModel):
    """Single recommendation item."""
    movie_id: int
    similarity_score: float

class RecommendationList(BaseModel):
    """List of recommendations for a user."""
    user_id: str
    recommendations: List[RecommendationItem]