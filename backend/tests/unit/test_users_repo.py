import pytest
from app.repositories.users_repo import UsersRepository

@pytest.fixture
def temp_users_repo(tmp_path):
    """Create a UsersRepository with a temporary CSV file."""
    users_file = tmp_path / "users.csv"
    user_repo = UsersRepository(users_file=users_file)
    return user_repo

def test_create_and_get_user(temp_users_repo):
    """Test that the user repo properly saves to a CSV file."""
    users_temp = temp_users_repo
    user_data = {
        "username": "bob",
        "email": "bob@example.com",
        "hashed_password": "supersecurepassword",
        "role": "user",
        "created_at": "2025-10-21T10:00:00"
    }
    created_user = users_temp.create(user_data)

    assert "id" in created_user
    user_id = created_user["id"]

    user_by_username = users_temp.get_by_username("bob")
    assert user_by_username is not None
    assert user_by_username["email"] == "bob@example.com"

    user_by_id = users_temp.get_by_id(user_id)
    assert user_by_id is not None
    assert user_by_id["username"] == "bob"