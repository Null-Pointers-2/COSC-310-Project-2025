"""Unit tests for users repository."""
import pytest
import csv
from app.repositories.users_repo import UsersRepository

@pytest.fixture
def temp_users_repo(tmp_path):
    """Create a UsersRepository with a temporary CSV file."""
    users_file = tmp_path / "users.csv"
    repo = UsersRepository(users_file=users_file)
    return repo, users_file

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "bob",
        "email": "bob@example.com",
        "hashed_password": "supersecurepassword",
        "role": "user",
        "created_at": "2025-10-21T10:00:00"
    }

def test_creates_file_if_not_exists(tmp_path):
    """Should create CSV file with headers if it doesn't exist."""
    users_file = tmp_path / "new_users.csv"
    assert not users_file.exists()
    
    repo = UsersRepository(users_file=users_file)
    
    assert users_file.exists()
    with users_file.open("r") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == UsersRepository.HEADERS

def test_does_not_overwrite_existing_file(tmp_path):
    """Should not overwrite existing file."""
    users_file = tmp_path / "existing_users.csv"
    users_file.write_text("id,username,email,hashed_password,role,created_at\n123,test,test@example.com,hash,user,2025-01-01\n")
    
    repo = UsersRepository(users_file=users_file)
    
    users = repo.get_all()
    assert len(users) == 1
    assert users[0]["username"] == "test"

def test_create_user_success(temp_users_repo, sample_user_data):
    """Should successfully create a user."""
    repo, _ = temp_users_repo
    
    created_user = repo.create(sample_user_data)
    
    assert "id" in created_user
    assert created_user["username"] == "bob"
    assert created_user["email"] == "bob@example.com"
    assert created_user["role"] == "user"

def test_create_user_generates_unique_id(temp_users_repo, sample_user_data):
    """Should generate unique IDs for each user."""
    repo, _ = temp_users_repo
    
    user1 = repo.create(sample_user_data)
    user2_data = {**sample_user_data, "username": "alice", "email": "alice@example.com"}
    user2 = repo.create(user2_data)
    
    assert user1["id"] != user2["id"]

def test_create_user_persists_to_file(temp_users_repo, sample_user_data):
    """Should persist user data to CSV file."""
    repo, users_file = temp_users_repo
    
    created_user = repo.create(sample_user_data)
    
    repo2 = UsersRepository(users_file=users_file)
    users = repo2.get_all()
    assert len(users) == 1
    assert users[0]["id"] == created_user["id"]

def test_get_by_id_success(temp_users_repo, sample_user_data):
    """Should retrieve user by ID."""
    repo, _ = temp_users_repo
    created_user = repo.create(sample_user_data)
    
    found_user = repo.get_by_id(created_user["id"])
    
    assert found_user is not None
    assert found_user["username"] == "bob"

def test_get_by_id_not_found(temp_users_repo):
    """Should return None for non-existent ID."""
    repo, _ = temp_users_repo
    
    found_user = repo.get_by_id("nonexistent-id")
    
    assert found_user is None

def test_get_by_username_success(temp_users_repo, sample_user_data):
    """Should retrieve user by username."""
    repo, _ = temp_users_repo
    repo.create(sample_user_data)
    
    found_user = repo.get_by_username("bob")
    
    assert found_user is not None
    assert found_user["email"] == "bob@example.com"

def test_get_by_username_not_found(temp_users_repo):
    """Should return None for non-existent username."""
    repo, _ = temp_users_repo
    
    found_user = repo.get_by_username("nonexistent")
    
    assert found_user is None

def test_get_by_email_success(temp_users_repo, sample_user_data):
    """Should retrieve user by email."""
    repo, _ = temp_users_repo
    repo.create(sample_user_data)
    
    found_user = repo.get_by_email("bob@example.com")
    
    assert found_user is not None
    assert found_user["username"] == "bob"

def test_get_by_email_not_found(temp_users_repo):
    """Should return None for non-existent email."""
    repo, _ = temp_users_repo
    
    found_user = repo.get_by_email("nonexistent@example.com")
    
    assert found_user is None

def test_get_all_returns_all_users(temp_users_repo, sample_user_data):
    """Should return all users."""
    repo, _ = temp_users_repo
    repo.create(sample_user_data)
    user2_data = {**sample_user_data, "username": "alice", "email": "alice@example.com"}
    repo.create(user2_data)
    
    all_users = repo.get_all()
    
    assert len(all_users) == 2

def test_get_all_returns_empty_list_when_no_users(temp_users_repo):
    """Should return empty list when no users exist."""
    repo, _ = temp_users_repo
    
    all_users = repo.get_all()
    
    assert all_users == []

def test_update_user_success(temp_users_repo, sample_user_data):
    """Should successfully update user."""
    repo, _ = temp_users_repo
    created_user = repo.create(sample_user_data)
    
    updated = repo.update(created_user["id"], {"email": "new@example.com"})
    
    assert updated is not None
    assert updated["email"] == "new@example.com"
    assert updated["username"] == "bob"  # Other fields unchanged

def test_update_user_not_found(temp_users_repo):
    """Should return None when updating non-existent user."""
    repo, _ = temp_users_repo
    
    updated = repo.update("nonexistent-id", {"email": "new@example.com"})
    
    assert updated is None

def test_update_preserves_id(temp_users_repo, sample_user_data):
    """Should preserve user ID after update."""
    repo, _ = temp_users_repo
    created_user = repo.create(sample_user_data)
    original_id = created_user["id"]
    
    updated = repo.update(original_id, {"email": "new@example.com"})
    
    assert updated["id"] == original_id

def test_update_persists_to_file(temp_users_repo, sample_user_data):
    """Should persist updates to file."""
    repo, users_file = temp_users_repo
    created_user = repo.create(sample_user_data)
    repo.update(created_user["id"], {"email": "updated@example.com"})
    
    repo2 = UsersRepository(users_file=users_file)
    found = repo2.get_by_id(created_user["id"])
    assert found is not None
    assert found["email"] == "updated@example.com"

def test_delete_user_success(temp_users_repo, sample_user_data):
    """Should successfully delete user."""
    repo, _ = temp_users_repo
    created_user = repo.create(sample_user_data)
    
    result = repo.delete(created_user["id"])
    
    assert result is True
    assert repo.get_by_id(created_user["id"]) is None

def test_delete_user_not_found(temp_users_repo):
    """Should return False when deleting non-existent user."""
    repo, _ = temp_users_repo
    
    result = repo.delete("nonexistent-id")
    
    assert result is False

def test_delete_persists_to_file(temp_users_repo, sample_user_data):
    """Should persist deletion to file."""
    repo, users_file = temp_users_repo
    created_user = repo.create(sample_user_data)
    repo.delete(created_user["id"])
    
    repo2 = UsersRepository(users_file=users_file)
    assert repo2.get_by_id(created_user["id"]) is None

def test_delete_only_removes_target_user(temp_users_repo, sample_user_data):
    """Should only delete the specified user."""
    repo, _ = temp_users_repo
    user1 = repo.create(sample_user_data)
    user2_data = {**sample_user_data, "username": "alice", "email": "alice@example.com"}
    user2 = repo.create(user2_data)
    
    repo.delete(user1["id"])
    
    assert repo.get_by_id(user1["id"]) is None
    assert repo.get_by_id(user2["id"]) is not None

def test_password_not_exposed_in_get_methods(temp_users_repo, sample_user_data):
    """Should include hashed_password in retrieved data (service layer filters it)."""
    repo, _ = temp_users_repo
    created_user = repo.create(sample_user_data)
    
    found_user = repo.get_by_id(created_user["id"])
    
    assert "hashed_password" in found_user
    assert found_user["hashed_password"] == "supersecurepassword"

def test_handles_special_characters_in_username(temp_users_repo):
    """Should handle special characters in username."""
    repo, _ = temp_users_repo
    user_data = {
        "username": "user@123!",
        "email": "test@example.com",
        "hashed_password": "hash",
        "role": "user",
        "created_at": "2025-01-01"
    }
    
    repo.create(user_data)
    found = repo.get_by_username("user@123!")
    
    assert found is not None
    assert found["username"] == "user@123!"