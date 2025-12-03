"""
Integration tests for authentication API endpoints.
"""

from datetime import UTC, datetime

import jwt
import pytest

from app.core.config import settings


@pytest.fixture
def auth_headers(client, clean_test_data):
    """Create a test user and return auth headers."""
    users_repo = clean_test_data["users_repo"]

    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!",
        },
    )
    response = client.post("/auth/login", data={"username": "testuser", "password": "SecurePass123!"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def registered_user(client, clean_test_data):
    """Create and return a registered user."""
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!",
        },
    )
    return response.json()


def test_register_success(client, clean_test_data):
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_username(client, clean_test_data):
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!",
        },
    )
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "different@example.com",
            "password": "SecurePass123!",
        },
    )

    assert response.status_code == 400
    assert "username" in response.json()["detail"].lower()
    assert "already registered" in response.json()["detail"].lower()


def test_register_duplicate_email(client, clean_test_data):
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!",
        },
    )
    response = client.post(
        "/auth/register",
        json={
            "username": "differentuser",
            "email": "test@example.com",
            "password": "SecurePass123!",
        },
    )
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()
    assert "already registered" in response.json()["detail"].lower()


def test_register_user_stored_in_database(client, clean_test_data):
    users_repo = clean_test_data["users_repo"]

    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!",
        },
    )
    assert response.status_code == 201
    user = users_repo.get_by_username("testuser")
    assert user is not None
    assert user["email"] == "test@example.com"
    assert user["hashed_password"] != "SecurePass123!"  # Password should be hashed


def test_login_success(client, registered_user):
    response = client.post("/auth/login", data={"username": "testuser", "password": "SecurePass123!"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


def test_login_returns_valid_jwt(client, registered_user):
    response = client.post("/auth/login", data={"username": "testuser", "password": "SecurePass123!"})
    token = response.json()["access_token"]
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == "testuser"


def test_login_wrong_password(client, registered_user):
    response = client.post("/auth/login", data={"username": "testuser", "password": "WrongPassword123!"})
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_login_nonexistent_user(client, clean_test_data):
    response = client.post("/auth/login", data={"username": "nonexistent", "password": "SecurePass123!"})
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_get_me_success(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_get_me_invalid_token(client, clean_test_data):
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token_string"})
    assert response.status_code == 401


def test_get_me_token_for_deleted_user(client, auth_headers, clean_test_data):
    users_repo = clean_test_data["users_repo"]

    user = users_repo.get_by_username("testuser")
    assert user is not None
    users_repo.delete(user["id"])
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 401
