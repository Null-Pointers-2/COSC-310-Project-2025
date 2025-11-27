"""Admin service for managing users and penalties."""

from collections import Counter
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.schemas.penalty import Penalty, PenaltyCreate


def get_all_users_with_stats(resources) -> list[dict]:
    """Get all users with statistics (admin only)."""
    users = resources.users_repo.get_all()
    all_ratings = resources.ratings_repo.get_all()
    all_penalties = resources.penalties_repo.get_all()

    users_with_stats = []
    for user in users:
        user_id = user["id"]

        rating_count = len([r for r in all_ratings if r["user_id"] == user_id])
        watchlist_count = len(resources.watchlist_repo.get_by_user(user_id))

        user_penalties = [p for p in all_penalties if p["user_id"] == user_id]
        active_penalties = [p for p in user_penalties if p["status"] == "active"]

        users_with_stats.append(
            {
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
                },
            },
        )

    return users_with_stats


def apply_penalty(resources, admin_id: str, penalty_data: PenaltyCreate) -> Penalty:
    """Apply a penalty to a user."""
    penalty_dict = {
        "user_id": penalty_data.user_id,
        "reason": penalty_data.reason,
        "description": penalty_data.description,
        "issued_by": admin_id,
    }

    created_penalty = resources.penalties_repo.create(penalty_dict)
    return Penalty(**created_penalty)


def get_all_penalties(resources) -> list[Penalty]:
    """Get all penalties (admin only)."""
    penalties = resources.penalties_repo.get_all()
    return [Penalty(**p) for p in penalties]


def get_user_penalties(resources, user_id: str) -> list[Penalty]:
    """Get penalties for a specific user."""
    penalties = resources.penalties_repo.get_by_user(user_id)
    return [Penalty(**p) for p in penalties]


def resolve_penalty(resources, penalty_id: str) -> bool:
    """Resolve a penalty."""
    return resources.penalties_repo.resolve(penalty_id)


def delete_penalty(resources, penalty_id: str) -> bool:
    """Delete a penalty."""
    return resources.penalties_repo.delete(penalty_id)


def get_system_stats(resources) -> dict:
    """Get system-wide statistics."""
    users = resources.users_repo.get_all()
    ratings = resources.ratings_repo.get_all()
    penalties = resources.penalties_repo.get_all()

    total_movies = len(resources.movies_repo.movies_df) if resources.movies_repo.movies_df is not None else 0
    active_penalties = [p for p in penalties if p["status"] == "active"]

    total_watchlist_items = sum(len(resources.watchlist_repo.get_by_user(user["id"])) for user in users)

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


def check_user_violations(resources, user_id: str) -> list[str]:
    """Check if user has any violations."""
    violations = []

    user_ratings = resources.ratings_repo.get_by_user(user_id)
    if not user_ratings:
        return violations

    # Spam (too many ratings in last hour)
    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)

    recent_ratings = [r for r in user_ratings if datetime.fromisoformat(r["timestamp"]) > one_hour_ago]

    if len(recent_ratings) > settings.MAX_RATINGS_FOR_SPAM_HOURLY:
        violations.append(f"Spam detected: {len(recent_ratings)} ratings in last hour")

    # Rating bombing (same rating given to many movies in short time)
    if len(recent_ratings) > settings.MAX_RATINGS_FOR_SPAM_HOURLY:
        rating_values = [r["rating"] for r in recent_ratings]
        most_common_rating = Counter(rating_values).most_common(1)[0]
        if most_common_rating[1] > settings.MAX_REPEAT_RATINGS_FOR_REVIEW_BOMBING:
            violations.append(
                f"Potential review bombing: {most_common_rating[1]} ratings of {most_common_rating[0]} in last hour"
            )

    # Suspicious patterns
    all_ratings = [r["rating"] for r in user_ratings]

    if len(all_ratings) >= settings.MIN_RATINGS_FOR_SUSPICIOUS_PATTERN:
        if all(r == settings.MIN_RATING for r in all_ratings):
            violations.append("Suspicious pattern: All ratings are 0.5 stars")
        elif all(r == settings.MAX_RATING for r in all_ratings):
            violations.append("Suspicious pattern: All ratings are 5.0 stars")

    return violations
