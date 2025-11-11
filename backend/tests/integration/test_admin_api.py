"""
Integration tests for admin API endpoints.
"""

from datetime import UTC, datetime

import jwt
import pytest

from app.core.config import settings
from app.repositories.penalties_repo import PenaltiesRepository
from app.repositories.ratings_repo import RatingsRepository
from app.repositories.users_repo import UsersRepository


users_repo = UsersRepository()
penalties_repo = PenaltiesRepository()
ratings_repo = RatingsRepository()


@pytest.fixture(autouse=True)
def cleanup_test_data():
    test_usernames = ["adminuser", "testuser", "penalizeduser"]
    test_emails = ["admin@example.com", "test@example.com", "penalized@example.com"]

    for username in test_usernames:
        user = users_repo.get_by_username(username)
        if user:
            user_ratings = ratings_repo.get_by_user(user["id"])
            for rating in user_ratings:
                ratings_repo.delete(rating["id"])
            users_repo.delete(user["id"])

    for email in test_emails:
        user = users_repo.get_by_email(email)
        if user:
            user_ratings = ratings_repo.get_by_user(user["id"])
            for rating in user_ratings:
                ratings_repo.delete(rating["id"])
            users_repo.delete(user["id"])

    yield

    for username in test_usernames:
        user = users_repo.get_by_username(username)
        if user:
            user_ratings = ratings_repo.get_by_user(user["id"])
            for rating in user_ratings:
                ratings_repo.delete(rating["id"])
            penalties = penalties_repo.get_by_user(user["id"])
            for penalty in penalties:
                penalties_repo.delete(penalty["id"])
            users_repo.delete(user["id"])

    for email in test_emails:
        user = users_repo.get_by_email(email)
        if user:
            user_ratings = ratings_repo.get_by_user(user["id"])
            for rating in user_ratings:
                ratings_repo.delete(rating["id"])
            penalties = penalties_repo.get_by_user(user["id"])
            for penalty in penalties:
                penalties_repo.delete(penalty["id"])
            users_repo.delete(user["id"])


@pytest.fixture
def admin_token(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "AdminPass123!",
        },
    )
    admin = response.json()

    users_repo.update(admin["id"], {"role": "admin"})

    payload = {"sub": "adminuser", "exp": datetime.now(UTC).timestamp() + 3600}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return token


@pytest.fixture
def regular_user(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
        },
    )
    return response.json()


@pytest.fixture
def regular_user_token(client):
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
        },
    )

    payload = {"sub": "testuser", "exp": datetime.now(UTC).timestamp() + 3600}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return token


def test_get_all_users_success(client, admin_token, regular_user):
    response = client.get("/admin/users", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # At least admin and regular user

    user_data = data[0]
    assert "id" in user_data
    assert "username" in user_data
    assert "stats" in user_data
    assert "rating_count" in user_data["stats"]
    assert "watchlist_count" in user_data["stats"]
    assert "total_penalties" in user_data["stats"]


def test_get_all_users_forbidden_for_regular_user(client, regular_user_token):
    response = client.get("/admin/users", headers={"Authorization": f"Bearer {regular_user_token}"})

    assert response.status_code == 403
    assert "Admin privileges required" in response.json()["detail"]


def test_get_all_users_unauthorized_without_token(client):
    response = client.get("/admin/users")

    assert response.status_code == 401


def test_apply_penalty_success(client, admin_token, regular_user):
    response = client.post(
        "/admin/penalties",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "user_id": regular_user["id"],
            "reason": "Spam",
            "description": "Posted 100 ratings in 1 minute",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == regular_user["id"]
    assert data["reason"] == "Spam"
    assert data["status"] == "active"
    assert "id" in data
    assert "issued_at" in data


def test_apply_penalty_forbidden_for_regular_user(client, regular_user_token):
    user = users_repo.get_by_username("testuser")
    assert user is not None

    response = client.post(
        "/admin/penalties",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={"user_id": user["id"], "reason": "Spam", "description": "Test"},
    )

    assert response.status_code == 403


def test_get_all_penalties_success(client, admin_token, regular_user):
    client.post(
        "/admin/penalties",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"user_id": regular_user["id"], "reason": "Spam", "description": "Test"},
    )

    response = client.get("/admin/penalties", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_all_penalties_forbidden_for_regular_user(client, regular_user_token):
    response = client.get("/admin/penalties", headers={"Authorization": f"Bearer {regular_user_token}"})

    assert response.status_code == 403


def test_get_user_penalties_success(client, admin_token, regular_user):
    client.post(
        "/admin/penalties",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"user_id": regular_user["id"], "reason": "Spam", "description": "Test"},
    )

    response = client.get(
        f"/admin/penalties/user/{regular_user['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["user_id"] == regular_user["id"]


def test_resolve_penalty_success(client, admin_token, regular_user):
    penalty_response = client.post(
        "/admin/penalties",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"user_id": regular_user["id"], "reason": "Spam", "description": "Test"},
    )
    penalty = penalty_response.json()

    response = client.put(
        f"/admin/penalties/{penalty['id']}/resolve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert "Penalty resolved successfully" in response.json()["message"]


def test_resolve_nonexistent_penalty_returns_404(client, admin_token):
    response = client.put(
        "/admin/penalties/non-existent-id/resolve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 404


def test_delete_penalty_success(client, admin_token, regular_user):
    penalty_response = client.post(
        "/admin/penalties",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"user_id": regular_user["id"], "reason": "Spam", "description": "Test"},
    )
    penalty = penalty_response.json()

    response = client.delete(
        f"/admin/penalties/{penalty['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 204


def test_delete_nonexistent_penalty_returns_404(client, admin_token):
    response = client.delete(
        "/admin/penalties/non-existent-id",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 404


def test_get_system_stats_success(client, admin_token, regular_user):
    response = client.get("/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_movies" in data
    assert "total_ratings" in data
    assert "total_penalties" in data
    assert "active_penalties" in data
    assert "avg_ratings_per_user" in data
    assert data["total_users"] >= 2  # At least admin and regular user


def test_check_user_violations_success(client, admin_token, regular_user):
    response = client.get(
        f"/admin/violations/{regular_user['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "violations" in data
    assert isinstance(data["violations"], list)


def test_penalized_user_blocked_from_access(client, admin_token, regular_user_token):
    user = users_repo.get_by_username("testuser")
    assert user is not None

    client.post(
        "/admin/penalties",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "user_id": user["id"],
            "reason": "Spam",
            "description": "Blocked for spam",
        },
    )

    response = client.post(
        "/ratings",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={"movie_id": 1, "rating": 4.0},
    )

    assert response.status_code == 403
    assert "active penalties" in response.json()["detail"].lower()


def test_user_can_access_after_penalty_resolved(client, admin_token, regular_user_token):
    user = users_repo.get_by_username("testuser")
    assert user is not None

    penalty_response = client.post(
        "/admin/penalties",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"user_id": user["id"], "reason": "Spam", "description": "Test"},
    )
    penalty = penalty_response.json()

    response = client.post(
        "/ratings",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={"movie_id": 100, "rating": 4.0},
    )
    assert response.status_code == 403

    client.put(
        f"/admin/penalties/{penalty['id']}/resolve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    response = client.post(
        "/ratings",
        headers={"Authorization": f"Bearer {regular_user_token}"},
        json={"movie_id": 101, "rating": 4.5},
    )
    assert response.status_code == 201
