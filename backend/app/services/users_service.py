"""User management service."""
from typing import List, Optional
from app.repositories.users_repo import UsersRepository
from app.repositories.ratings_repo import RatingsRepository
from app.repositories.penalties_repo import PenaltiesRepository
from app.repositories.recommendations_repo import RecommendationsRepository
from app.schemas.user import UserProfile, UserDashboard

RECENT_MOVIE_VIEW_LIMIT = 7
RECOMMENDED_MOVIE_VIEW_LIMIT = 3

users_repo = UsersRepository()
ratings_repo = RatingsRepository()
penalties_repo = PenaltiesRepository()
recommendations_repo = RecommendationsRepository()

def get_user_by_id(user_id: str) -> Optional[dict]:
    """Get user by ID."""
    user_dict = users_repo.get_by_id(user_id)
    if not user_dict:
        return None
    return user_dict

def get_user_profile(user_id: str) -> UserProfile:
    """Get user profile with statistics."""
    user = get_user_by_id(user_id)
    if not user:
        return None
    
    user_ratings = ratings_repo.get_by_user(user_id)
    user_penalties = penalties_repo.get_by_user(user_id)

    total_ratings = len(user_ratings)
    average_rating = 0.0
    if total_ratings > 0:
        average_rating = sum(r['rating'] for r in user_ratings) / total_ratings

    profile_data = {
        "id": user["user_id"], 
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "created_at": user["created_at"], 
        "total_ratings": total_ratings,
        "average_rating": round(average_rating, 2),
        "active_penalties": len(user_penalties)
    }

    return UserProfile(**profile_data)

def get_user_dashboard(user_id: str) -> UserDashboard:
    """Get user dashboard data."""
    # TODO: Compile user profile, recent ratings, recommendations, penalties
    profile = get_user_profile(user_id)
    if not profile:
        return None
    
    recent_ratings = ratings_repo.get_by_user(user_id, limit=RECENT_MOVIE_VIEW_LIMIT)
    penalties = penalties_repo.get_by_user(user_id)
    
    recommendations = recommendations_repo.get_for_user(user_id, limit=RECOMMENDED_MOVIE_VIEW_LIMIT)
    
    dashboard_data = {
        "user": profile,
        "recent_ratings": recent_ratings,
        "recommendations": recommendations,
        "penalties": penalties
    }

    return UserDashboard(**dashboard_data)

def update_user(user_id: str, update_data: dict) -> dict:
    """Update user information."""
    update_dict = update_data.model_dump(exclude_unset=True)
    
    if not update_dict:
        return get_user_by_id(user_id)
    
    updated_user = users_repo.update(user_id, update_dict)
    return updated_user

def get_all_users() -> List[dict]:
    """Get all users (admin only)."""
    return users_repo.get_all()