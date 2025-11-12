"""Unit tests for watchlist service."""

from unittest.mock import Mock

import pytest

from app.schemas.watchlist import WatchlistItemCreate
from app.services import watchlist_service


@pytest.fixture
def mock_resources():
    resources = Mock()
    resources.watchlist_repo = Mock()
    resources.movies_repo = Mock()
    return resources


@pytest.fixture
def sample_movie():
    return {"movieId": 1, "title": "The Matrix (1999)", "genres": ["Action", "Sci-Fi"]}


def test_returns_empty_list_for_user_with_no_watchlist(mock_resources):
    mock_resources.watchlist_repo.get_by_user.return_value = []

    result = watchlist_service.get_user_watchlist(mock_resources, "user123")

    assert result == []
    mock_resources.watchlist_repo.get_by_user.assert_called_once_with("user123")


def test_returns_watchlist_with_valid_movies(mock_resources, sample_movie):
    mock_resources.watchlist_repo.get_by_user.return_value = [1, 2]
    mock_resources.movies_repo.get_by_id.side_effect = [
        {"movieId": 1, "title": "Movie 1"},
        {"movieId": 2, "title": "Movie 2"},
    ]

    result = watchlist_service.get_user_watchlist(mock_resources, "user123")

    assert len(result) == 2
    assert result[0].user_id == "user123"
    assert result[0].movie_id == 1
    assert result[1].movie_id == 2


def test_filters_out_invalid_movies(mock_resources):
    mock_resources.watchlist_repo.get_by_user.return_value = [1, 999, 2]
    mock_resources.movies_repo.get_by_id.side_effect = [
        {"movieId": 1, "title": "Movie 1"},
        None,  # Movie 999 doesn't exist
        {"movieId": 2, "title": "Movie 2"},
    ]

    result = watchlist_service.get_user_watchlist(mock_resources, "user123")

    assert len(result) == 2
    assert all(item.movie_id in [1, 2] for item in result)


def test_returns_items_for_correct_user(mock_resources):
    mock_resources.watchlist_repo.get_by_user.return_value = [1, 2]
    mock_resources.movies_repo.get_by_id.side_effect = [
        {"movieId": 1, "title": "Movie 1"},
        {"movieId": 2, "title": "Movie 2"},
    ]

    result = watchlist_service.get_user_watchlist(mock_resources, "user456")

    mock_resources.watchlist_repo.get_by_user.assert_called_once_with("user456")
    assert all(item.user_id == "user456" for item in result)


def test_successfully_adds_movie_to_watchlist(mock_resources, sample_movie):
    mock_resources.movies_repo.get_by_id.return_value = sample_movie
    mock_resources.watchlist_repo.exists.return_value = False
    mock_resources.watchlist_repo.add.return_value = {
        "user_id": "user123",
        "movie_id": 1,
    }

    item_create = WatchlistItemCreate(movie_id=1)
    result = watchlist_service.add_to_watchlist(mock_resources, "user123", item_create)

    assert result.user_id == "user123"
    assert result.movie_id == 1
    mock_resources.watchlist_repo.add.assert_called_once_with("user123", 1)


def test_raises_error_when_movie_not_found(mock_resources):
    mock_resources.movies_repo.get_by_id.return_value = None

    item_create = WatchlistItemCreate(movie_id=999)

    with pytest.raises(ValueError, match="Movie with ID 999 not found"):
        watchlist_service.add_to_watchlist(mock_resources, "user123", item_create)

    mock_resources.watchlist_repo.add.assert_not_called()


def test_raises_error_when_movie_already_in_watchlist(mock_resources, sample_movie):
    mock_resources.movies_repo.get_by_id.return_value = sample_movie
    mock_resources.watchlist_repo.exists.return_value = True

    item_create = WatchlistItemCreate(movie_id=1)

    with pytest.raises(ValueError, match="Movie already in watchlist"):
        watchlist_service.add_to_watchlist(mock_resources, "user123", item_create)

    mock_resources.watchlist_repo.add.assert_not_called()


def test_checks_movie_existence_before_adding(mock_resources, sample_movie):
    mock_resources.movies_repo.get_by_id.return_value = sample_movie
    mock_resources.watchlist_repo.exists.return_value = False
    mock_resources.watchlist_repo.add.return_value = {
        "user_id": "user123",
        "movie_id": 1,
    }

    item_create = WatchlistItemCreate(movie_id=1)
    watchlist_service.add_to_watchlist(mock_resources, "user123", item_create)

    mock_resources.movies_repo.get_by_id.assert_called_once_with(1)


def test_checks_duplicate_before_adding(mock_resources, sample_movie):
    mock_resources.movies_repo.get_by_id.return_value = sample_movie
    mock_resources.watchlist_repo.exists.return_value = False
    mock_resources.watchlist_repo.add.return_value = {
        "user_id": "user123",
        "movie_id": 1,
    }

    item_create = WatchlistItemCreate(movie_id=1)
    watchlist_service.add_to_watchlist(mock_resources, "user123", item_create)

    mock_resources.watchlist_repo.exists.assert_called_once_with("user123", 1)


def test_successfully_removes_movie(mock_resources):
    mock_resources.watchlist_repo.remove.return_value = True

    result = watchlist_service.remove_from_watchlist(mock_resources, "user123", 1)

    assert result is True
    mock_resources.watchlist_repo.remove.assert_called_once_with("user123", 1)


def test_removes_correct_movie_for_correct_user(mock_resources):
    mock_resources.watchlist_repo.remove.return_value = True

    watchlist_service.remove_from_watchlist(mock_resources, "user456", 5)

    mock_resources.watchlist_repo.remove.assert_called_once_with("user456", 5)


def test_returns_true_when_movie_in_watchlist(mock_resources):
    mock_resources.watchlist_repo.exists.return_value = True

    result = watchlist_service.is_in_watchlist(mock_resources, "user123", 1)

    assert result is True
    mock_resources.watchlist_repo.exists.assert_called_once_with("user123", 1)


def test_checks_for_correct_user_and_movie(mock_resources):
    mock_resources.watchlist_repo.exists.return_value = True

    watchlist_service.is_in_watchlist(mock_resources, "user789", 42)

    mock_resources.watchlist_repo.exists.assert_called_once_with("user789", 42)


def test_handles_empty_watchlist_gracefully(mock_resources):
    mock_resources.watchlist_repo.get_by_user.return_value = []

    result = watchlist_service.get_user_watchlist(mock_resources, "user123")

    assert result == []
    assert isinstance(result, list)


def test_handles_all_invalid_movies_in_watchlist(mock_resources):
    mock_resources.watchlist_repo.get_by_user.return_value = [999, 888, 777]
    mock_resources.movies_repo.get_by_id.return_value = None

    result = watchlist_service.get_user_watchlist(mock_resources, "user123")

    assert result == []


def test_handles_mixed_valid_invalid_movies(mock_resources):
    mock_resources.watchlist_repo.get_by_user.return_value = [1, 999, 2, 888]

    def get_movie_side_effect(movie_id):
        if movie_id in [1, 2]:
            return {"movieId": movie_id, "title": f"Movie {movie_id}"}
        return None

    mock_resources.movies_repo.get_by_id.side_effect = get_movie_side_effect

    result = watchlist_service.get_user_watchlist(mock_resources, "user123")

    assert len(result) == 2
    assert {item.movie_id for item in result} == {1, 2}


def test_add_movie_with_integer_conversion(mock_resources, sample_movie):
    mock_resources.movies_repo.get_by_id.return_value = sample_movie
    mock_resources.watchlist_repo.exists.return_value = False
    mock_resources.watchlist_repo.add.return_value = {
        "user_id": "user123",
        "movie_id": 1,
    }

    item_create = WatchlistItemCreate(movie_id=1)
    result = watchlist_service.add_to_watchlist(mock_resources, "user123", item_create)
    assert result.movie_id == 1
