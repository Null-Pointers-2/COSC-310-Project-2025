"""
Integration tests for admin API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
import jwt
from app.main import app
from app.core.config import settings
from app.repositories.users_repo import UsersRepository
from app.repositories.penalties_repo import PenaltiesRepository
from app.repositories.ratings_repo import RatingsRepository

users_repo = UsersRepository()
penalties_repo = PenaltiesRepository()
ratings_repo = RatingsRepository()

@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data before and after each test."""
    test_usernames = ["adminuser", "testuser", "penalizeduser"]
    test_emails = [
        "admin@example.com",
        "test@example.com",
        "penalized@example.com"
    ]

    # Clean up users
    for username in test_usernames:
        user = users_repo.get_by_username(username)
        if user:
            # Clean up ratings for this user
            user_ratings = ratings_repo.get_by_user(user["id"])
            for rating in user_ratings:
                ratings_repo.delete(rating["id"])
            users_repo.delete(user["id"])

    for email in test_emails:
        user = users_repo.get_by_email(email)
        if user:
            # Clean up ratings for this user
            user_ratings = ratings_repo.get_by_user(user["id"])
            for rating in user_ratings:
                ratings_repo.delete(rating["id"])
            users_repo.delete(user["id"])

    yield

    # Clean up after test
    for username in test_usernames:
        user = users_repo.get_by_username(username)
        if user:
            # Clean up ratings for this user
            user_ratings = ratings_repo.get_by_user(user["id"])
            for rating in user_ratings:
                ratings_repo.delete(rating["id"])
            # Clean up penalties for this user
            penalties = penalties_repo.get_by_user(user["id"])
            for penalty in penalties:
                penalties_repo.delete(penalty["id"])
            users_repo.delete(user["id"])

    for email in test_emails:
        user = users_repo.get_by_email(email)
        if user:
            # Clean up ratings for this user
            user_ratings = ratings_repo.get_by_user(user["id"])
            for rating in user_ratings:
                ratings_repo.delete(rating["id"])
            penalties = penalties_repo.get_by_user(user["id"])
            for penalty in penalties:
                penalties_repo.delete(penalty["id"])
            users_repo.delete(user["id"])

@pytest.fixture
def admin_token(client):
    """Create an admin user and return auth token."""
    # Register admin user
    response = client.post(
        "/auth/register",
        json={
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "AdminPass123!"
        }
    )
    admin = response.json()

    # Update user to admin role
    users_repo.update(admin["id"], {"role": "admin"})

    # Generate token
    payload = {
        "sub": "adminuser",
        "exp": datetime.now(timezone.utc).timestamp() + 3600
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return token

@pytest.fixture
def regular_user(client):
    """Create a regular user and return user data."""
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!"
        }
    )
    return response.json()

@pytest.fixture
def regular_user_token(client):
    """Create a regular user and return auth token."""
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!"
        }
    )

    payload = {
        "sub": "testuser",
        "exp": datetime.now(timezone.utc).timestamp() + 3600
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return token


class TestGetAllUsersEndpoint:
    """Test GET /admin/users endpoint."""

    def test_get_all_users_success(self, client, admin_token, regular_user):
        """Test admin can get all users with stats."""
        response = client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # At least admin and regular user

        # Check structure
        user_data = data[0]
        assert "id" in user_data
        assert "username" in user_data
        assert "stats" in user_data
        assert "rating_count" in user_data["stats"]
        assert "watchlist_count" in user_data["stats"]
        assert "total_penalties" in user_data["stats"]

    def test_get_all_users_forbidden_for_regular_user(self, client, regular_user_token):
        """Test regular users cannot access admin endpoint."""
        response = client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )

        assert response.status_code == 403
        assert "Admin privileges required" in response.json()["detail"]

    def test_get_all_users_unauthorized_without_token(self, client):
        """Test endpoint requires authentication."""
        response = client.get("/admin/users")

        assert response.status_code == 401


class TestApplyPenaltyEndpoint:
    """Test POST /admin/penalties endpoint."""

    def test_apply_penalty_success(self, client, admin_token, regular_user):
        """Test admin can apply penalty to user."""
        response = client.post(
            "/admin/penalties",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "user_id": regular_user["id"],
                "reason": "Spam",
                "description": "Posted 100 ratings in 1 minute"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == regular_user["id"]
        assert data["reason"] == "Spam"
        assert data["status"] == "active"
        assert "id" in data
        assert "issued_at" in data

    def test_apply_penalty_forbidden_for_regular_user(self, client, regular_user_token):
        """Test regular users cannot apply penalties."""
        # Get the user who owns the token
        user = users_repo.get_by_username("testuser")

        response = client.post(
            "/admin/penalties",
            headers={"Authorization": f"Bearer {regular_user_token}"},
            json={
                "user_id": user["id"],
                "reason": "Spam",
                "description": "Test"
            }
        )

        assert response.status_code == 403


class TestGetAllPenaltiesEndpoint:
    """Test GET /admin/penalties endpoint."""

    def test_get_all_penalties_success(self, client, admin_token, regular_user):
        """Test admin can get all penalties."""
        # Create a penalty first
        client.post(
            "/admin/penalties",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "user_id": regular_user["id"],
                "reason": "Spam",
                "description": "Test"
            }
        )

        response = client.get(
            "/admin/penalties",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_all_penalties_forbidden_for_regular_user(self, client, regular_user_token):
        """Test regular users cannot view all penalties."""
        response = client.get(
            "/admin/penalties",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )

        assert response.status_code == 403


class TestGetUserPenaltiesEndpoint:
    """Test GET /admin/penalties/user/{user_id} endpoint."""

    def test_get_user_penalties_success(self, client, admin_token, regular_user):
        """Test admin can get penalties for specific user."""
        # Create a penalty
        client.post(
            "/admin/penalties",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "user_id": regular_user["id"],
                "reason": "Spam",
                "description": "Test"
            }
        )

        response = client.get(
            f"/admin/penalties/user/{regular_user['id']}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["user_id"] == regular_user["id"]


class TestResolvePenaltyEndpoint:
    """Test PUT /admin/penalties/{penalty_id}/resolve endpoint."""

    def test_resolve_penalty_success(self, client, admin_token, regular_user):
        """Test admin can resolve a penalty."""
        # Create a penalty
        penalty_response = client.post(
            "/admin/penalties",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "user_id": regular_user["id"],
                "reason": "Spam",
                "description": "Test"
            }
        )
        penalty = penalty_response.json()

        response = client.put(
            f"/admin/penalties/{penalty['id']}/resolve",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        assert "Penalty resolved successfully" in response.json()["message"]

    def test_resolve_nonexistent_penalty_returns_404(self, client, admin_token):
        """Test resolving non-existent penalty returns 404."""
        response = client.put(
            "/admin/penalties/non-existent-id/resolve",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 404


class TestDeletePenaltyEndpoint:
    """Test DELETE /admin/penalties/{penalty_id} endpoint."""

    def test_delete_penalty_success(self, client, admin_token, regular_user):
        """Test admin can delete a penalty."""
        # Create a penalty
        penalty_response = client.post(
            "/admin/penalties",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "user_id": regular_user["id"],
                "reason": "Spam",
                "description": "Test"
            }
        )
        penalty = penalty_response.json()

        response = client.delete(
            f"/admin/penalties/{penalty['id']}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 204

    def test_delete_nonexistent_penalty_returns_404(self, client, admin_token):
        """Test deleting non-existent penalty returns 404."""
        response = client.delete(
            "/admin/penalties/non-existent-id",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 404


class TestGetSystemStatsEndpoint:
    """Test GET /admin/stats endpoint."""

    def test_get_system_stats_success(self, client, admin_token, regular_user):
        """Test admin can get system statistics."""
        response = client.get(
            "/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_movies" in data
        assert "total_ratings" in data
        assert "total_penalties" in data
        assert "active_penalties" in data
        assert "avg_ratings_per_user" in data
        assert data["total_users"] >= 2  # At least admin and regular user


class TestCheckUserViolationsEndpoint:
    """Test GET /admin/violations/{user_id} endpoint."""

    def test_check_user_violations_success(self, client, admin_token, regular_user):
        """Test admin can check user violations."""
        response = client.get(
            f"/admin/violations/{regular_user['id']}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "violations" in data
        assert isinstance(data["violations"], list)


class TestPenaltyEnforcement:
    """Test that penalties block user access."""

    def test_penalized_user_blocked_from_access(self, client, admin_token, regular_user_token):
        """Test that user with active penalty cannot access endpoints."""
        # Get the user who owns the token
        user = users_repo.get_by_username("testuser")

        # Apply penalty to user
        client.post(
            "/admin/penalties",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "user_id": user["id"],
                "reason": "Spam",
                "description": "Blocked for spam"
            }
        )

        # Try to access an endpoint that requires active user
        response = client.post(
            "/ratings",
            headers={"Authorization": f"Bearer {regular_user_token}"},
            json={
                "movie_id": 1,
                "rating": 4.0
            }
        )

        assert response.status_code == 403
        assert "active penalties" in response.json()["detail"].lower()

    def test_user_can_access_after_penalty_resolved(self, client, admin_token, regular_user_token):
        """Test that user can access after penalty is resolved."""
        # Get the user who owns the token
        user = users_repo.get_by_username("testuser")

        # Apply penalty
        penalty_response = client.post(
            "/admin/penalties",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "user_id": user["id"],
                "reason": "Spam",
                "description": "Test"
            }
        )
        penalty = penalty_response.json()

        # Verify user is blocked
        response = client.post(
            "/ratings",
            headers={"Authorization": f"Bearer {regular_user_token}"},
            json={
                "movie_id": 100,
                "rating": 4.0
            }
        )
        assert response.status_code == 403

        # Resolve penalty
        client.put(
            f"/admin/penalties/{penalty['id']}/resolve",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Verify user can now access
        response = client.post(
            "/ratings",
            headers={"Authorization": f"Bearer {regular_user_token}"},
            json={
                "movie_id": 101,
                "rating": 4.5
            }
        )
        assert response.status_code == 201
