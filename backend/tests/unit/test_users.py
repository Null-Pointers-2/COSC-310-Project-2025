import pytest
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.core.dependencies import get_current_user, get_current_admin_user

mock_user_dict = {
    "user_id": "user123",
    "username": "testuser",
    "email": "user@example.com",
    "role": "user"
}

mock_admin_dict = {
    "user_id": "admin456",
    "username": "adminuser",
    "email": "admin@example.com",
    "role": "admin"
}

mock_user_profile = {
    "id": "user123",
    "username": "testuser",
    "email": "user@example.com",
    "role": "user",
    "created_at": "2025-01-01T12:00:00Z",
    "total_ratings": 10,
    "average_rating": 3.5,
    "penalties_count": 1
}


# Override functions to bypass auth for testings
def override_get_current_user():
    return mock_user_dict

def override_get_current_admin_user():
    return mock_admin_dict

@pytest.fixture
def auth_client(test_app):
    """Client with auth dependencies overridden."""
    test_app.dependency_overrides[get_current_user] = override_get_current_user
    test_app.dependency_overrides[get_current_admin_user] = override_get_current_admin_user

    with TestClient(test_app) as test_client:
        yield test_client

    test_app.dependency_overrides = {}


def test_get_my_profile_success(auth_client, monkeypatch):
    monkeypatch.setattr(
        "app.services.users_service.get_user_profile",
        lambda *args, **kwargs: mock_user_profile
    )

    response = auth_client.get("/users/me")

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert response_data["id"] == mock_user_profile["id"]
    assert response_data["username"] == mock_user_profile["username"]
    assert response_data["total_ratings"] == 10
    assert response_data["average_rating"] == 3.5

def test_get_my_profile_not_found(auth_client, monkeypatch):
    monkeypatch.setattr(
        "app.services.users_service.get_user_profile",
        lambda *args, **kwargs: None
    )

    response = auth_client.get("/users/me")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User profile not found"