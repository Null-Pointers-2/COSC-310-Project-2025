import pytest
from app.services import users_service
from app.schemas.user import UserUpdate

mock_user_repo = {
    "id": "user123",
    "username": "testuser",
    "email": "user@example.com",
    "role": "user",
    "created_at": "2025-01-01T12:00:00Z"
}

mock_ratings_from_repo = [
    {"rating": 4},
    {"rating": 5},
    {"rating": 3}
]

mock_penalties_from_repo = [
    {"reason": "Late submission", "status": "active"}
]

mock_recommendations_from_repo = [
    {"movie_id": "movie123", "title": "Test Movie"}
]

def test_get_user_profile_success(mocker):
    mocker.patch("app.services.users_service.users_repo.get_by_id", return_value=mock_user_repo)
    mocker.patch("app.services.users_service.ratings_repo.get_by_user", return_value=mock_ratings_from_repo)
    mocker.patch("app.services.users_service.penalties_repo.get_by_user", return_value=mock_penalties_from_repo)

    profile = users_service.get_user_profile(user_id="user123")

    assert profile is not None

    assert profile.total_ratings == 3
    assert profile.average_rating == 4.0  
    assert profile.active_penalties == 1

    assert profile.id == "user123"
    assert profile.username == "testuser"

def test_get_user_profile_not_found(mocker):
    mocker.patch("app.services.users_service.users_repo.get_by_id", return_value=None)
    
    profile = users_service.get_user_profile(user_id="nonexistent")
    
    assert profile is None

def test_get_user_dashboard_success(mocker):
    mocker.patch("app.services.users_service.users_repo.get_by_id", return_value=mock_user_repo)
    mocker.patch("app.services.users_service.ratings_repo.get_by_user", return_value=mock_ratings_from_repo)
    mocker.patch("app.services.users_service.penalties_repo.get_by_user", return_value=mock_penalties_from_repo)
    # TODO: Uncomment after recommendations_repo implementation
    # mocker.patch("app.services.users_service.recommendations_repo.get_for_user", return_value=mock_recommendations_from_repo)
    
    dashboard = users_service.get_user_dashboard(user_id="user123")
    
    assert dashboard is not None
    assert dashboard.user.id == "user123"
    assert len(dashboard.recent_ratings) == 3
    assert len(dashboard.penalties) == 1
    assert len(dashboard.recommendations) == 0  # TODO: Adjust when recommendations_repo is implemented

def test_get_all_users(mocker):
    mock_user_list = [mock_user_repo, mock_user_repo]
    mocker.patch("app.services.users_service.users_repo.get_all", return_value=mock_user_list)
    
    users = users_service.get_all_users()
    
    assert len(users) == 2
    assert users[0]["username"] == "testuser"

def test_update_user(mocker):
    mock_update_method = mocker.patch("app.services.users_service.users_repo.update", return_value={"id": "user123", "email": "new@email.com"})
    
    update_data = UserUpdate(email="new@email.com")
    
    users_service.update_user(user_id="user123", update_data=update_data)
    
    expected_update_dict = {"email": "new@email.com"}
    mock_update_method.assert_called_once_with("user123", expected_update_dict)

def test_update_user_no_data(mocker):
    mock_update_method = mocker.patch("app.services.users_service.users_repo.update")
    mock_get_method = mocker.patch("app.services.users_service.users_repo.get_by_id", return_value=mock_user_repo)

    update_data = UserUpdate() 
    
    result = users_service.update_user(user_id="user123", update_data=update_data)
    
    mock_update_method.assert_not_called()
    mock_get_method.assert_called_once_with("user123")
    assert result["username"] == "testuser"