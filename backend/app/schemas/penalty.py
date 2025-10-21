"""Penalty schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PenaltyBase(BaseModel):
    """Base penalty schema."""
    user_id: str
    reason: str = Field(..., max_length=500)
    description: Optional[str] = None

class PenaltyCreate(PenaltyBase):
    """Schema for creating a penalty."""
    pass

class Penalty(PenaltyBase):
    """Complete penalty schema."""
    id: str
    status: str  # "active", "resolved"
    issued_at: datetime
    resolved_at: Optional[datetime] = None
    issued_by: str  # admin user_id
    
    class Config:
        from_attributes = True