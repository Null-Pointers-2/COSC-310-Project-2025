"""Unit tests for admin service."""
import pytest
import csv
from datetime import datetime, timezone, timedelta
from pathlib import Path
from app.services import admin_service
from app.repositories.users_repo import UsersRepository
from app.repositories.penalties_repo import PenaltiesRepository
from app.repositories.ratings_repo import RatingsRepository
from app.repositories.watchlist_repo import WatchlistRepository
from app.schemas.penalty import PenaltyCreate

@pytest.fixture
def setup_repos(tmp_path, monkeypatch):
    """Setup temporary repositories for testing."""
    users_file = tmp_path / "users.csv"
    penalties_file = tmp_path / "penalties.json"
    ratings_file = tmp_path / "ratings.json"
    watchlist_file = tmp_path / "watchlist.json"

    users_repo = UsersRepository(users_file=str(users_file))
    penalties_repo = PenaltiesRepository(penalties_file=str(penalties_file))
    ratings_repo = RatingsRepository(ratings_file=str(ratings_file))
    watchlist_repo = WatchlistRepository(watchlist_file=str(watchlist_file))

    monkeypatch.setattr(admin_service, "users_repo", users_repo)
    monkeypatch.setattr(admin_service, "penalties_repo", penalties_repo)
    monkeypatch.setattr(admin_service, "ratings_repo", ratings_repo)
    monkeypatch.setattr(admin_service, "watchlist_repo", watchlist_repo)

    return {
        "users": users_repo,
        "penalties": penalties_repo,
        "ratings": ratings_repo,
        "watchlist": watchlist_repo
    }

def test_get_all_users_with_stats(setup_repos):
    """Test getting all users with statistics."""
    repos = setup_repos

    # Create test users
    user1 = repos["users"].create({
        "username": "user1",
        "email": "user1@test.com",
        "hashed_password": "hash1",
        "role": "user",
        "created_at": "2025-01-01"
    })
    user2 = repos["users"].create({
        "username": "user2",
        "email": "user2@test.com",
        "hashed_password": "hash2",
        "role": "user",
        "created_at": "2025-01-02"
    })

    # Add ratings for user1
    repos["ratings"].create({"user_id": user1["id"], "movie_id": 1, "rating": 4.0})
    repos["ratings"].create({"user_id": user1["id"], "movie_id": 2, "rating": 5.0})

    # Add watchlist for user1
    repos["watchlist"].add(user1["id"], 10)

    # Add penalty for user1
    repos["penalties"].create({
        "user_id": user1["id"],
        "reason": "Spam",
        "description": None,
        "issued_by": "admin1"
    })

    users_with_stats = admin_service.get_all_users_with_stats()

    assert len(users_with_stats) == 2

    user1_stats = next(u for u in users_with_stats if u["username"] == "user1")
    assert user1_stats["stats"]["rating_count"] == 2
    assert user1_stats["stats"]["watchlist_count"] == 1
    assert user1_stats["stats"]["total_penalties"] == 1
    assert user1_stats["stats"]["active_penalties"] == 1

    user2_stats = next(u for u in users_with_stats if u["username"] == "user2")
    assert user2_stats["stats"]["rating_count"] == 0
    assert user2_stats["stats"]["watchlist_count"] == 0
    assert user2_stats["stats"]["total_penalties"] == 0

def test_apply_penalty(setup_repos):
    """Test applying a penalty to a user."""
    repos = setup_repos

    user = repos["users"].create({
        "username": "testuser",
        "email": "test@test.com",
        "hashed_password": "hash",
        "role": "user",
        "created_at": "2025-01-01"
    })

    penalty_data = PenaltyCreate(
        user_id=user["id"],
        reason="Spam",
        description="Posted 100 ratings in 1 minute"
    )

    result = admin_service.apply_penalty("admin1", penalty_data)

    assert result.user_id == user["id"]
    assert result.reason == "Spam"
    assert result.status == "active"
    assert result.issued_by == "admin1"

def test_get_all_penalties(setup_repos):
    """Test getting all penalties."""
    repos = setup_repos

    repos["penalties"].create({
        "user_id": "user1",
        "reason": "Spam",
        "description": None,
        "issued_by": "admin1"
    })
    repos["penalties"].create({
        "user_id": "user2",
        "reason": "Harassment",
        "description": None,
        "issued_by": "admin1"
    })

    penalties = admin_service.get_all_penalties()

    assert len(penalties) == 2
    assert all(hasattr(p, "user_id") for p in penalties)
    assert all(hasattr(p, "reason") for p in penalties)

def test_get_user_penalties(setup_repos):
    """Test getting penalties for a specific user."""
    repos = setup_repos

    repos["penalties"].create({
        "user_id": "user1",
        "reason": "Spam",
        "description": None,
        "issued_by": "admin1"
    })
    repos["penalties"].create({
        "user_id": "user1",
        "reason": "Harassment",
        "description": None,
        "issued_by": "admin1"
    })
    repos["penalties"].create({
        "user_id": "user2",
        "reason": "Spam",
        "description": None,
        "issued_by": "admin1"
    })

    user1_penalties = admin_service.get_user_penalties("user1")

    assert len(user1_penalties) == 2
    assert all(p.user_id == "user1" for p in user1_penalties)

def test_resolve_penalty(setup_repos):
    """Test resolving a penalty."""
    repos = setup_repos

    created = repos["penalties"].create({
        "user_id": "user1",
        "reason": "Spam",
        "description": None,
        "issued_by": "admin1"
    })

    success = admin_service.resolve_penalty(created["id"])

    assert success is True

    resolved = repos["penalties"].get_by_id(created["id"])
    assert resolved["status"] == "resolved"

def test_delete_penalty(setup_repos):
    """Test deleting a penalty."""
    repos = setup_repos

    created = repos["penalties"].create({
        "user_id": "user1",
        "reason": "Spam",
        "description": None,
        "issued_by": "admin1"
    })

    success = admin_service.delete_penalty(created["id"])

    assert success is True
    assert repos["penalties"].get_by_id(created["id"]) is None

def test_get_system_stats(setup_repos):
    """Test getting system-wide statistics."""
    repos = setup_repos

    # Create users
    user1 = repos["users"].create({
        "username": "user1",
        "email": "user1@test.com",
        "hashed_password": "hash",
        "role": "user",
        "created_at": "2025-01-01"
    })
    user2 = repos["users"].create({
        "username": "user2",
        "email": "user2@test.com",
        "hashed_password": "hash",
        "role": "user",
        "created_at": "2025-01-02"
    })

    # Create ratings
    repos["ratings"].create({"user_id": user1["id"], "movie_id": 1, "rating": 4.0})
    repos["ratings"].create({"user_id": user1["id"], "movie_id": 2, "rating": 5.0})
    repos["ratings"].create({"user_id": user2["id"], "movie_id": 3, "rating": 3.0})

    # Create penalties
    repos["penalties"].create({
        "user_id": user1["id"],
        "reason": "Spam",
        "description": None,
        "issued_by": "admin1"
    })

    # Add watchlist items
    repos["watchlist"].add(user1["id"], 10)
    repos["watchlist"].add(user2["id"], 20)

    stats = admin_service.get_system_stats()

    assert stats["total_users"] == 2
    assert stats["total_ratings"] == 3
    assert stats["total_penalties"] == 1
    assert stats["active_penalties"] == 1
    assert stats["total_watchlist_items"] == 2
    assert stats["avg_ratings_per_user"] == 1.5

def test_check_user_violations_spam(setup_repos):
    """Test detecting spam violations (>50 ratings in 1 hour)."""
    repos = setup_repos

    user = repos["users"].create({
        "username": "spammer",
        "email": "spam@test.com",
        "hashed_password": "hash",
        "role": "user",
        "created_at": "2025-01-01"
    })

    # Create 60 ratings in the last hour
    now = datetime.now(timezone.utc)
    for i in range(60):
        rating = repos["ratings"].create({
            "user_id": user["id"],
            "movie_id": i,
            "rating": 4.0
        })
        # Manually update timestamp to be recent
        all_ratings = repos["ratings"]._read()
        for r in all_ratings:
            if r["id"] == rating["id"]:
                r["timestamp"] = now.isoformat()
        repos["ratings"]._write(all_ratings)

    violations = admin_service.check_user_violations(user["id"])

    assert len(violations) > 0
    assert any("Spam detected" in v for v in violations)

def test_check_user_violations_all_same_rating(setup_repos):
    """Test detecting suspicious patterns (all same extreme ratings)."""
    repos = setup_repos

    user = repos["users"].create({
        "username": "suspicious",
        "email": "sus@test.com",
        "hashed_password": "hash",
        "role": "user",
        "created_at": "2025-01-01"
    })

    # Create 15 ratings all with 5.0
    for i in range(15):
        repos["ratings"].create({
            "user_id": user["id"],
            "movie_id": i,
            "rating": 5.0
        })

    violations = admin_service.check_user_violations(user["id"])

    assert len(violations) > 0
    assert any("Suspicious pattern" in v and "5.0" in v for v in violations)

def test_check_user_violations_no_violations(setup_repos):
    """Test that normal users have no violations."""
    repos = setup_repos

    user = repos["users"].create({
        "username": "normal",
        "email": "normal@test.com",
        "hashed_password": "hash",
        "role": "user",
        "created_at": "2025-01-01"
    })

    # Create a few normal ratings
    repos["ratings"].create({"user_id": user["id"], "movie_id": 1, "rating": 4.0})
    repos["ratings"].create({"user_id": user["id"], "movie_id": 2, "rating": 3.5})
    repos["ratings"].create({"user_id": user["id"], "movie_id": 3, "rating": 5.0})

    violations = admin_service.check_user_violations(user["id"])

    assert len(violations) == 0
