"""Unit tests for users service."""
import pytest
from unittest.mock import Mock
from app.services import users_service
from app.schemas.user import UserUpdate

@pytest.fixture
def mock_resources():
    resources = Mock()
    resources.users_repo = Mock()
    resources.ratings_repo = Mock()
    resources.penalties_repo = Mock()
    resources.recommendations_repo = Mock()
    return resources

@pytest.fixture
def sample_user():
    return {
        "id": "user123",
        "username": "testuser",
        "email": "user@example.com",
        "role": "user",
        "created_at": "2025-01-01T12:00:00Z"
    }

@pytest.fixture
def sample_ratings():
    return [
        {"rating": 4.0},
        {"rating": 5.0},
        {"rating": 3.0}
    ]

@pytest.fixture
def sample_penalties():
    return [
        {"reason": "Late submission", "status": "active"}
    ]

def test_returns_user_when_found(mock_resources, sample_user):
    mock_resources.users_repo.get_by_id.return_value = sample_user
    
    result = users_service.get_user_by_id("user123", mock_resources)
    
    assert result == sample_user
    mock_resources.users_repo.get_by_id.assert_called_once_with("user123")

def test_returns_none_when_not_found(mock_resources):
    mock_resources.users_repo.get_by_id.return_value = None
    
    result = users_service.get_user_by_id("nonexistent", mock_resources)
    
    assert result is None

def test_profile_success(mock_resources, sample_user, sample_ratings, sample_penalties):
    mock_resources.users_repo.get_by_id.return_value = sample_user
    mock_resources.ratings_repo.get_by_user.return_value = sample_ratings
    mock_resources.penalties_repo.get_by_user.return_value = sample_penalties

    profile = users_service.get_user_profile("user123", mock_resources)

    assert profile is not None
    assert profile.id == "user123"
    assert profile.username == "testuser"
    assert profile.total_ratings == 3
    assert profile.average_rating == 4.0
    assert profile.active_penalties == 1

def test_profile_not_found(mock_resources):
    mock_resources.users_repo.get_by_id.return_value = None

    profile = users_service.get_user_profile("nonexistent", mock_resources)

    assert profile is None

def test_profile_with_no_ratings(mock_resources, sample_user):
    mock_resources.users_repo.get_by_id.return_value = sample_user
    mock_resources.ratings_repo.get_by_user.return_value = []
    mock_resources.penalties_repo.get_by_user.return_value = []

    profile = users_service.get_user_profile("user123", mock_resources)

    assert profile is not None
    assert profile.total_ratings == 0
    assert profile.average_rating == 0.0


def test_dashboard_success(mock_resources, sample_user, sample_ratings, sample_penalties):
    mock_resources.users_repo.get_by_id.return_value = sample_user
    mock_resources.ratings_repo.get_by_user.return_value = sample_ratings
    mock_resources.penalties_repo.get_by_user.return_value = sample_penalties
    mock_resources.recommendations_repo.get_for_user.return_value = {
        "user_id": "user123",
        "recommendations": [
            {"movie_id": 1, "similarity_score": 0.9}
        ]
    }

    dashboard = users_service.get_user_dashboard("user123", mock_resources)

    assert dashboard is not None
    assert dashboard.user.id == "user123"
    assert len(dashboard.recent_ratings) == 3
    assert len(dashboard.penalties) == 1
    assert dashboard.recommendations is not None

def test_dashboard_not_found(mock_resources):
    mock_resources.users_repo.get_by_id.return_value = None

    dashboard = users_service.get_user_dashboard("nonexistent", mock_resources)

    assert dashboard is None

def test_update_with_data(mock_resources, sample_user):
    updated_user = {**sample_user, "email": "new@email.com"}
    mock_resources.users_repo.update.return_value = updated_user

    update_data = UserUpdate(email="new@email.com")
    result = users_service.update_user("user123", update_data, mock_resources)

    expected_update_dict = {"email": "new@email.com"}
    mock_resources.users_repo.update.assert_called_once_with("user123", expected_update_dict)
    assert result is not None
    assert result["email"] == "new@email.com"

def test_update_with_no_data(mock_resources, sample_user):
    mock_resources.users_repo.get_by_id.return_value = sample_user

    update_data = UserUpdate()
    result = users_service.update_user("user123", update_data, mock_resources)

    mock_resources.users_repo.update.assert_not_called()
    mock_resources.users_repo.get_by_id.assert_called_once_with("user123")
    assert result is not None
    assert result["username"] == "testuser"

def test_returns_all_users(mock_resources, sample_user):
    mock_user_list = [sample_user, {**sample_user, "id": "user456", "username": "anotheruser"}]
    mock_resources.users_repo.get_all.return_value = mock_user_list

    users = users_service.get_all_users(mock_resources)

    assert len(users) == 2
    assert users[0]["username"] == "testuser"
    assert users[1]["username"] == "anotheruser"
    mock_resources.users_repo.get_all.assert_called_once()