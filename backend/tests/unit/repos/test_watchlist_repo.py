"""Unit tests for watchlist repository."""

import json

import pytest

from app.repositories.watchlist_repo import WatchlistRepository


@pytest.fixture
def mock_store():
    """A dictionary to act as the 'file' in memory."""
    return {}


@pytest.fixture
def mock_repo(mocker, mock_store):
    """
    Creates a repository with Path mocked out.
    Reads/Writes are redirected to the 'mock_store' dictionary.
    """
    mock_path_cls = mocker.patch("app.repositories.watchlist_repo.Path")
    mock_path_instance = mock_path_cls.return_value

    mock_path_instance.exists.return_value = True

    mock_path_instance.read_text.side_effect = lambda: json.dumps(mock_store)

    def fake_dump(data, fp, indent=None):
        mock_store.clear()
        mock_store.update(data)

    mocker.patch("app.repositories.watchlist_repo.json.dump", side_effect=fake_dump)

    repo = WatchlistRepository(watchlist_file="dummy.json")

    repo._mock_path = mock_path_instance

    return repo, mock_store


def test_file_is_created_if_not_exists(mocker):
    """
    Test that checks if the file creation logic runs when exists() returns False.
    """
    mock_path_cls = mocker.patch("app.repositories.watchlist_repo.Path")
    mock_path_instance = mock_path_cls.return_value

    mock_path_instance.exists.return_value = False

    WatchlistRepository(watchlist_file="new_file.json")

    mock_path_instance.exists.assert_called_once()
    mock_path_instance.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
    mock_path_instance.write_text.assert_called_once_with("{}")


def test_create_user_add_movie(mock_repo):
    repo, store = mock_repo

    result = repo.add("user1", 1)

    assert result == {"user_id": "user1", "movie_id": 1}
    assert "user1" in store
    assert 1 in store["user1"]


def test_add_multiple_movies_same_user(mock_repo):
    repo, store = mock_repo

    repo.add("user1", 1)
    repo.add("user1", 2)
    repo.add("user1", 3)

    assert len(store["user1"]) == 3
    assert set(store["user1"]) == {1, 2, 3}


def test_get_by_user(mock_repo):
    repo, _ = mock_repo

    repo.add("user1", 1)
    repo.add("user1", 2)
    repo.add("user2", 3)

    user1_watchlist = repo.get_by_user("user1")
    user2_watchlist = repo.get_by_user("user2")
    unknown_user_watchlist = repo.get_by_user("jonesy")

    assert set(user1_watchlist) == {1, 2}
    assert user2_watchlist == [3]
    assert unknown_user_watchlist == []


def test_get_by_user_empty_list_for_new_user(mock_repo):
    repo, _ = mock_repo

    result = repo.get_by_user("new_user")
    assert result == []
    assert isinstance(result, list)


def test_add_prevents_duplicates(mock_repo):
    repo, store = mock_repo

    repo.add("user1", 1)
    repo.add("user1", 1)
    repo.add("user1", 1)

    assert store["user1"].count(1) == 1


def test_remove_movies(mock_repo):
    repo, store = mock_repo

    repo.add("user1", 1)
    repo.add("user1", 2)
    repo.add("user2", 3)

    result = repo.remove("user1", 1)

    assert result is True
    assert 1 not in store["user1"]
    assert 2 in store["user1"]
    assert 3 in store["user2"]


def test_remove_movie_not_found(mock_repo):
    repo, _ = mock_repo

    repo.add("user1", 1)
    result = repo.remove("user1", 999)

    assert result is False


def test_remove_movie_user_not_found(mock_repo):
    repo, _ = mock_repo

    result = repo.remove("user_nonexistent", 1)
    assert result is False


def test_remove_last_movie_keeps_user_entry(mock_repo):
    repo, store = mock_repo

    repo.add("user1", 1)
    repo.remove("user1", 1)

    assert "user1" in store
    assert store["user1"] == []


def test_exists(mock_repo):
    repo, _ = mock_repo

    repo.add("user1", 1)

    assert repo.exists("user1", 1) is True
    assert repo.exists("user1", 2) is False
    assert repo.exists("tim apple", 1) is False


def test_exists_empty_watchlist(mock_repo):
    repo, _ = mock_repo

    assert repo.exists("user1", 1) is False


def test_remove_from_middle_of_list(mock_repo):
    repo, store = mock_repo

    repo.add("user1", 1)
    repo.add("user1", 2)
    repo.add("user1", 3)
    repo.add("user1", 4)

    repo.remove("user1", 2)

    assert 2 not in store["user1"]
    assert set(store["user1"]) == {1, 3, 4}


def test_exists_after_remove(mock_repo):
    repo, _ = mock_repo

    repo.add("user1", 1)
    assert repo.exists("user1", 1) is True

    repo.remove("user1", 1)
    assert repo.exists("user1", 1) is False
