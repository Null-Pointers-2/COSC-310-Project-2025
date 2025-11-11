"""Unit tests for watchlist repository."""
import json
import pytest
from app.repositories.watchlist_repo import WatchlistRepository

@pytest.fixture
def temp_watchlist(tmp_path):
    """Create a temporary WatchlistRepository with an isolated JSON file."""
    file_path = tmp_path / "watchlist.json"
    repo = WatchlistRepository(watchlist_file=str(file_path))
    return repo, file_path

def test_file_is_created_if_not_exists(temp_watchlist):
    """Test that watchlist file is created with empty object if it doesn't exist."""
    repo, file_path = temp_watchlist

    assert file_path.exists()
    assert json.loads(file_path.read_text()) == {}

def test_create_user_add_movie(temp_watchlist):
    """Test adding a movie to a new user's watchlist."""
    repo, file_path = temp_watchlist

    result = repo.add("user1", 1)
    data = json.loads(file_path.read_text())

    assert result == {"user_id": "user1", "movie_id": 1}
    assert "user1" in data
    assert 1 in data["user1"]

def test_add_multiple_movies_same_user(temp_watchlist):
    """Test adding multiple movies to the same user's watchlist."""
    repo, file_path = temp_watchlist

    repo.add("user1", 1)
    repo.add("user1", 2)
    repo.add("user1", 3)

    data = json.loads(file_path.read_text())
    assert len(data["user1"]) == 3
    assert set(data["user1"]) == {1, 2, 3}

def test_get_by_user(temp_watchlist):
    """Test that get_by_user() returns the correct movies for each user."""
    repo, file_path = temp_watchlist

    repo.add("user1", 1)
    repo.add("user1", 2)
    repo.add("user2", 3)

    user1_watchlist = repo.get_by_user("user1")
    user2_watchlist = repo.get_by_user("user2")
    unknown_user_watchlist = repo.get_by_user("jonesy")

    assert set(user1_watchlist) == {1, 2}
    assert user2_watchlist == [3]
    assert unknown_user_watchlist == []

def test_get_by_user_empty_list_for_new_user(temp_watchlist):
    """Test that get_by_user returns empty list for user with no watchlist."""
    repo, _ = temp_watchlist

    result = repo.get_by_user("new_user")
    assert result == []
    assert isinstance(result, list)

def test_add_prevents_duplicates(temp_watchlist):
    """Test that movies cannot be added multiple times for the same user."""
    repo, file_path = temp_watchlist

    repo.add("user1", 1)
    repo.add("user1", 1)
    repo.add("user1", 1)

    data = json.loads(file_path.read_text())
    assert data["user1"].count(1) == 1

def test_remove_movies(temp_watchlist):
    """Test that a movie that exists can be removed."""
    repo, file_path = temp_watchlist

    repo.add("user1", 1)
    repo.add("user1", 2)
    repo.add("user2", 3)

    result = repo.remove("user1", 1)
    data = json.loads(file_path.read_text())

    assert result is True
    assert 1 not in data["user1"]
    assert 2 in data["user1"]
    assert 3 in data["user2"]

def test_remove_movie_not_found(temp_watchlist):
    """Test that a movie that is not found is not 'removed'."""
    repo, file_path = temp_watchlist

    repo.add("user1", 1)
    result = repo.remove("user1", 999) # Former site of 💯 from when IDs were strings, RIP

    assert result is False

def test_remove_movie_user_not_found(temp_watchlist):
    """Test removing movie for user that doesn't exist."""
    repo, _ = temp_watchlist

    result = repo.remove("user_nonexistent", 1)
    assert result is False

def test_remove_last_movie_keeps_user_entry(temp_watchlist):
    """Test that removing the last movie keeps the user's empty list."""
    repo, file_path = temp_watchlist

    repo.add("user1", 1)
    repo.remove("user1", 1)

    data = json.loads(file_path.read_text())
    assert "user1" in data
    assert data["user1"] == []

def test_exists(temp_watchlist):
    """Test if exists only returns true for present entries."""
    repo, file_path = temp_watchlist

    repo.add("user1", 1)

    assert repo.exists("user1", 1) is True
    assert repo.exists("user1", 2) is False
    assert repo.exists("tim apple", 1) is False

def test_exists_empty_watchlist(temp_watchlist):
    """Test exists returns False for empty watchlist."""
    repo, _ = temp_watchlist

    assert repo.exists("user1", 1) is False

def test_persistence_across_instances(tmp_path):
    """Test that data persists across repository instances."""
    file_path = tmp_path / "watchlist.json"
    
    repo1 = WatchlistRepository(watchlist_file=str(file_path))
    repo1.add("user1", 1)
    repo1.add("user1", 2)
    
    repo2 = WatchlistRepository(watchlist_file=str(file_path))
    watchlist = repo2.get_by_user("user1")
    
    assert set(watchlist) == {1, 2}

def test_remove_from_middle_of_list(temp_watchlist):
    """Test removing a movie from the middle of a watchlist."""
    repo, file_path = temp_watchlist

    repo.add("user1", 1)
    repo.add("user1", 2)
    repo.add("user1", 3)
    repo.add("user1", 4)

    repo.remove("user1", 2)

    data = json.loads(file_path.read_text())
    assert 2 not in data["user1"]
    assert set(data["user1"]) == {1, 3, 4}

def test_exists_after_remove(temp_watchlist):
    """Test that exists returns False after movie is removed."""
    repo, _ = temp_watchlist

    repo.add("user1", 1)
    assert repo.exists("user1", 1) is True

    repo.remove("user1", 1)
    assert repo.exists("user1", 1) is False