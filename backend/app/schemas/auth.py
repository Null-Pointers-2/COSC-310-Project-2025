"""Authentication schemas."""
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Data stored in JWT token."""
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None