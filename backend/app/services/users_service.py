"""User management service."""
from typing import List, Optional
from app.schemas.user import UserProfile, UserDashboard, UserUpdate

RECENT_MOVIE_VIEW_LIMIT = 7
RECOMMENDED_MOVIE_VIEW_LIMIT = 3

def get_user_by_id(user_id: str, resources) -> Optional[dict]:
    """Get user by ID."""
    user_dict = resources.users_repo.get_by_id(user_id)
    if not user_dict:
        return None
    return user_dict

def get_user_profile(user_id: str, resources) -> Optional[UserProfile]:
    """Get user profile with statistics."""
    user = get_user_by_id(user_id, resources)
    if not user:
        return None

    user_ratings = resources.ratings_repo.get_by_user(user_id)
    user_penalties = resources.penalties_repo.get_by_user(user_id)

    total_ratings = len(user_ratings)
    average_rating = 0.0
    if total_ratings > 0:
        average_rating = sum(r['rating'] for r in user_ratings) / total_ratings

    profile_data = {
        "id": user["id"], 
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "created_at": user["created_at"], 
        "total_ratings": total_ratings,
        "average_rating": round(average_rating, 2),
        "active_penalties": len([p for p in user_penalties if p["status"] == "active"])
    }

    return UserProfile(**profile_data)

def get_user_dashboard(user_id: str, resources) -> Optional[UserDashboard]:
    """Get user dashboard data."""
    profile = get_user_profile(user_id, resources)
    if not profile:
        return None
    
    recent_ratings = resources.ratings_repo.get_by_user(user_id, limit=RECENT_MOVIE_VIEW_LIMIT)
    penalties = resources.penalties_repo.get_by_user(user_id)
    recommendations = resources.recommendations_repo.get_for_user(user_id)
    
    dashboard_data = {
        "user": profile,
        "recent_ratings": recent_ratings,
        "recommendations": recommendations,
        "penalties": penalties
    }

    return UserDashboard(**dashboard_data)

def update_user(user_id: str, update_data: UserUpdate, resources) -> Optional[dict]:
    """Update user information."""
    update_dict = update_data.model_dump(exclude_unset=True)

    if not update_dict:
        return get_user_by_id(user_id, resources)

    updated_user = resources.users_repo.update(user_id, update_dict)
    return updated_user

def get_all_users(resources) -> List[dict]:
    """Get all users (admin only)."""
    return resources.users_repo.get_all()