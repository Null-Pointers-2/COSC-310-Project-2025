"""Penalty schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PenaltyBase(BaseModel):
    """Base penalty schema."""

    user_id: str
    reason: str = Field(..., max_length=500)
    description: str | None = None


class PenaltyCreate(PenaltyBase):
    """Schema for creating a penalty."""


class Penalty(PenaltyBase):
    """Complete penalty schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str  # "active", "resolved"
    issued_at: datetime
    resolved_at: datetime | None = None
    issued_by: str  # admin user_id
