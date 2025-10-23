import pytest
from app.repositories.users_repo import UsersRepository

@pytest.fixture
def temp_users_repo(tmp_path):
    """Create a UsersRepository with a temporary CSV file."""
    users_file = tmp_path / "users.csv"
    repo = UsersRepository(users_file=users_file)
    return repo

def test_create_and_get_user(temp_users_repo):
    repo = temp_users_repo

    user_data = {
        "username": "bob",
        "email": "bob@example.com",
        "hashed_password": "supersecurepassword",
        "role": "user",
        "created_at": "2025-10-21T10:00:00"
    }
    created_user = repo.create(user_data)

    assert "id" in created_user
    user_id = created_user["id"]

    user_by_username = repo.get_by_username("bob")
    assert user_by_username is not None
    assert user_by_username["email"] == "bob@example.com"

    user_by_id = repo.get_by_id(user_id)
    assert user_by_id is not None
    assert user_by_id["username"] == "bob"