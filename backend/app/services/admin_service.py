"""Admin service for managing users and penalties."""
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from collections import Counter
from app.repositories.users_repo import UsersRepository
from app.repositories.penalties_repo import PenaltiesRepository
from app.repositories.ratings_repo import RatingsRepository
from app.repositories.watchlist_repo import WatchlistRepository
from app.repositories.movies_repo import MoviesRepository
from app.schemas.penalty import Penalty, PenaltyCreate

users_repo = UsersRepository()
penalties_repo = PenaltiesRepository()
ratings_repo = RatingsRepository()
watchlist_repo = WatchlistRepository()
movies_repo = MoviesRepository()

def get_all_users_with_stats() -> List[dict]:
    """Get all users with statistics (admin only)."""
    users = users_repo.get_all()
    all_ratings = ratings_repo.get_all()
    all_penalties = penalties_repo.get_all()

    users_with_stats = []
    for user in users:
        user_id = user["id"]

        rating_count = len([r for r in all_ratings if r["user_id"] == user_id])
        watchlist_count = len(watchlist_repo.get_by_user(user_id))

        user_penalties = [p for p in all_penalties if p["user_id"] == user_id]
        active_penalties = [p for p in user_penalties if p["status"] == "active"]

        users_with_stats.append({
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "created_at": user["created_at"],
            "stats": {
                "rating_count": rating_count,
                "watchlist_count": watchlist_count,
                "total_penalties": len(user_penalties),
                "active_penalties": len(active_penalties),
            }
        })

    return users_with_stats

def apply_penalty(admin_id: str, penalty_data: PenaltyCreate) -> Penalty:
    """Apply a penalty to a user."""
    penalty_dict = {
        "user_id": penalty_data.user_id,
        "reason": penalty_data.reason,
        "description": penalty_data.description,
        "issued_by": admin_id,
    }

    created_penalty = penalties_repo.create(penalty_dict)
    return Penalty(**created_penalty)

def get_all_penalties() -> List[Penalty]:
    """Get all penalties (admin only)."""
    penalties = penalties_repo.get_all()
    return [Penalty(**p) for p in penalties]

def get_user_penalties(user_id: str) -> List[Penalty]:
    """Get penalties for a specific user."""
    penalties = penalties_repo.get_by_user(user_id)
    return [Penalty(**p) for p in penalties]

def resolve_penalty(penalty_id: str) -> bool:
    """Resolve a penalty."""
    return penalties_repo.resolve(penalty_id)

def delete_penalty(penalty_id: str) -> bool:
    """Delete a penalty."""
    return penalties_repo.delete(penalty_id)

def get_system_stats() -> dict:
    """Get system-wide statistics."""
    users = users_repo.get_all()
    ratings = ratings_repo.get_all()
    penalties = penalties_repo.get_all()

    total_movies = len(movies_repo.movies_df) if movies_repo.movies_df is not None else 0
    active_penalties = [p for p in penalties if p["status"] == "active"]

    total_watchlist_items = sum(
        len(watchlist_repo.get_by_user(user["id"])) for user in users
    )

    avg_ratings_per_user = len(ratings) / len(users) if users else 0

    return {
        "total_users": len(users),
        "total_movies": total_movies,
        "total_ratings": len(ratings),
        "total_penalties": len(penalties),
        "active_penalties": len(active_penalties),
        "total_watchlist_items": total_watchlist_items,
        "avg_ratings_per_user": round(avg_ratings_per_user, 2),
    }

def check_user_violations(user_id: str) -> List[str]:
    """Check if user has any violations."""
    violations = []

    user_ratings = ratings_repo.get_by_user(user_id)

    if not user_ratings:
        return violations

    # Check for spam (more than 50 ratings in last hour)
    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)

    recent_ratings = [
        r for r in user_ratings
        if datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00")) > one_hour_ago
    ]

    if len(recent_ratings) > 50:
        violations.append(f"Spam detected: {len(recent_ratings)} ratings in last hour")

    # Check for rating bombing (same rating given to many movies in short time)
    if len(recent_ratings) > 10:
        rating_values = [r["rating"] for r in recent_ratings]
        most_common_rating = Counter(rating_values).most_common(1)[0]
        if most_common_rating[1] > 20:
            violations.append(
                f"Potential review bombing: {most_common_rating[1]} ratings of {most_common_rating[0]} in last hour"
            )

    # Check for suspicious patterns (all 0.5s or all 5.0s)
    all_ratings = [r["rating"] for r in user_ratings]
    if len(all_ratings) >= 10:
        if all(r == 0.5 for r in all_ratings):
            violations.append("Suspicious pattern: All ratings are 0.5 stars")
        elif all(r == 5.0 for r in all_ratings):
            violations.append("Suspicious pattern: All ratings are 5.0 stars")

    return violations