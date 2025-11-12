"""
Integration tests for users API endpoints.
"""

from datetime import UTC, datetime

import pytest

from app.core.dependencies import get_current_admin_user, get_current_user
from app.main import app
from app.schemas.user import UserCreate

MOCK_USER_ID = "test-user-123"
MOCK_ADMIN_ID = "admin-user-456"
MOCK_USER_EMAIL = "user@test.com"
MOCK_ADMIN_EMAIL = "admin@test.com"
MOCK_USER_PASSWORD = "securepassword"
MOCK_USER_USERNAME = "testuser"
MOCK_ADMIN_USERNAME = "testadmin"

MOCK_USER_UPDATE_PAYLOAD = {"email": "updated@test.com"}


@pytest.fixture
def override_current_user():
    def mock_get_current_user():
        return {"id": MOCK_USER_ID, "email": MOCK_USER_EMAIL}

    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    del app.dependency_overrides[get_current_user]


@pytest.fixture
def override_current_admin():
    def mock_get_current_admin():
        return {"id": MOCK_ADMIN_ID, "email": MOCK_ADMIN_EMAIL, "is_admin": True}

    app.dependency_overrides[get_current_admin_user] = mock_get_current_admin
    yield
    del app.dependency_overrides[get_current_admin_user]


@pytest.fixture(autouse=True)
def setup_users(test_repositories, clean_test_data):
    users_repo = test_repositories.get("users_repo")

    now = datetime.now(UTC).isoformat()

    user_data = UserCreate(
        email=MOCK_USER_EMAIL,
        password=MOCK_USER_PASSWORD,
        username=MOCK_USER_USERNAME,
    ).model_dump()

    user_data.pop("password")

    user_data["id"] = MOCK_USER_ID
    user_data["role"] = "user"
    user_data["created_at"] = now
    users_repo.create(user_data)

    admin_data = UserCreate(
        email=MOCK_ADMIN_EMAIL,
        password=MOCK_USER_PASSWORD,
        username=MOCK_ADMIN_USERNAME,
    ).model_dump()

    admin_data.pop("password")

    admin_data["id"] = MOCK_ADMIN_ID
    admin_data["role"] = "admin"
    admin_data["created_at"] = now
    users_repo.create(admin_data)


def test_get_my_profile_success(client, override_current_user):
    response = client.get("/users/me")

    assert response.status_code == 200
    assert response.json()["id"] == MOCK_USER_ID
    assert response.json()["username"] == MOCK_USER_USERNAME
    assert "total_ratings" in response.json()
    assert response.json()["total_ratings"] == 0


def test_get_my_dashboard_success(client, override_current_user):
    response = client.get("/users/me/dashboard")

    assert response.status_code == 200
    assert response.json()["user"]["id"] == MOCK_USER_ID
    assert "recent_ratings" in response.json()
    assert response.json()["recent_ratings"] == []


def test_update_my_profile_success(client, override_current_user):
    response = client.put("/users/me", json=MOCK_USER_UPDATE_PAYLOAD)

    assert response.status_code == 200
    assert response.json()["email"] == MOCK_USER_UPDATE_PAYLOAD["email"]
    assert response.json()["username"] == MOCK_USER_USERNAME


def test_update_my_profile_validation_error(client, override_current_user):
    invalid_data = {"email": "super-evil-invalid-email"}

    response = client.put("/users/me", json=invalid_data)

    assert response.status_code == 422


def test_get_all_users_success(client, override_current_admin):
    response = client.get("/users")

    assert response.status_code == 200
    assert len(response.json()) == 2
    emails = [u["email"] for u in response.json()]
    assert MOCK_USER_EMAIL in emails
    assert MOCK_ADMIN_EMAIL in emails


def test_get_user_profile_by_id_success(client, override_current_admin):
    response = client.get(f"/users/{MOCK_USER_ID}")

    assert response.status_code == 200
    assert response.json()["id"] == MOCK_USER_ID
    assert response.json()["username"] == MOCK_USER_USERNAME


def test_get_user_profile_by_id_not_found(client, override_current_admin):
    target_user_id = "non-existent-user-id"

    response = client.get(f"/users/{target_user_id}")

    assert response.status_code == 404
    assert "User profile not found" in response.json()["detail"]
