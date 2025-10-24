import json
from pathlib import Path
import pytest
from app.repositories.watchlist_repo import WatchlistRepository

@pytest.fixture
def temp_watchlist(tmp_path):
    """Create a temporary WatchlistRepository with an isolated JSON file."""
    file_path = tmp_path / "watchlist.json"
    repo = WatchlistRepository(watchlist_file=str(file_path))
    return repo, file_path

def test_file_is_created_if_not_exists(temp_watchlist):
    repo, file_path = temp_watchlist

    # File should exist and be empty JSON array
    assert file_path.exists()
    assert json.loads(file_path.read_text()) == {}

def test_create_user_add_movie(temp_watchlist):
    repo, file_path = temp_watchlist # Pytest fixture

    result = repo.add("user1", "movie1")
    data = json.loads(file_path.read_text())

    assert result == {"user_id": "user1", "movie_id": "movie1"}
    assert "user1" in data
    assert "movie1" in data["user1"]

def test_get_by_user(temp_watchlist): # Test that get_by_user() returns the correct movies for each user.
    repo, file_path = temp_watchlist

    repo.add("user1", "movie1")
    repo.add("user1", "movie2")
    repo.add("user2", "movie3")

    user1_watchlist = repo.get_by_user("user1")
    user2_watchlist = repo.get_by_user("user2")
    unknown_user_watchlist = repo.get_by_user("jonesy") # not in repo

    assert set(user1_watchlist) == {"movie1", "movie2"}
    assert user2_watchlist == ["movie3"]
    assert unknown_user_watchlist == []

def test_add_prevents_duplicates(temp_watchlist): # Test that movies can not be added multiple times for the same user
    repo, file_path = temp_watchlist

    repo.add("user1", "movie1")
    repo.add("user1", "movie1")

    data = json.loads(file_path.read_text())
    assert data["user1"].count("movie1") == 1

def test_remove_movies(temp_watchlist): # Test that a movie that exists can be removed
    repo, file_path = temp_watchlist

    repo.add("user1", "movie1")
    repo.add("user2", "movie2")

    result = repo.remove("user1", "movie1")
    data = json.loads(file_path.read_text())

    assert result is True
    assert "movie1" not in data["user1"]
    assert "movie2" in data["user2"]

def test_remove_movie_not_found(temp_watchlist): # Test that a movie that is not found is not "removed"
    repo, file_path = temp_watchlist

    repo.add("user1", "movie1")
    result = repo.remove("user1", "100 emoji") # not in the repo

    assert result is False


def test_exists(temp_watchlist): # Test if exists only returns true for present entries
    repo, file_path = temp_watchlist

    repo.add("user1", "movie1")

    assert repo.exists("user1", "movie1") is True
    assert repo.exists("user1", "movie2") is False # movie not in repo
    assert repo.exists("tim apple", "movie 1") is False # user not in repo



