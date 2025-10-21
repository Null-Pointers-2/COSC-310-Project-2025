"""User management service."""
from typing import List, Optional
from app.repositories.users_repo import UsersRepository
from app.repositories.ratings_repo import RatingsRepository
from app.repositories.penalties_repo import PenaltiesRepository
from app.schemas.user import UserProfile, UserDashboard

users_repo = UsersRepository()
ratings_repo = RatingsRepository()
penalties_repo = PenaltiesRepository()

def get_user_by_id(user_id: str) -> Optional[dict]:
    """Get user by ID."""
    user_dict = users_repo.get_by_id(user_id)
    if not user_dict:
        raise ValueError("User not found")

def get_user_profile(user_id: str) -> UserProfile:
    """Get user profile with statistics."""
    # TODO: Get user, calculate stats from ratings and penalties
    pass

def get_user_dashboard(user_id: str) -> UserDashboard:
    """Get user dashboard data."""
    # TODO: Compile user profile, recent ratings, recommendations, penalties
    pass

def update_user(user_id: str, update_data: dict) -> dict:
    """Update user information."""
    # TODO: Implement
    pass

def get_all_users() -> List[dict]:
    """Get all users (admin only)."""
    # TODO: Implement
    pass