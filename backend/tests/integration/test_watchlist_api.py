"""
Integration tests for watchlist API endpoints.
"""

from datetime import UTC, datetime, timezone
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from app.routers import watchlist
from app.schemas.watchlist import WatchlistItem, WatchlistItemCreate


@pytest.fixture
def mock_resources():
    return Mock()


@pytest.fixture
def mock_current_user():
    return {"id": "user123", "username": "testuser", "role": "user"}


@pytest.fixture
def sample_watchlist_item():
    """
    Creates a valid WatchlistItem with the required added_at field.
    """
    return WatchlistItem(user_id="user123", movie_id=1, added_at=datetime.now(UTC))


def test_get_my_watchlist_success(mock_resources, mock_current_user, sample_watchlist_item):
    mock_watchlist = [sample_watchlist_item]

    with patch("app.routers.watchlist.watchlist_service.get_user_watchlist", return_value=mock_watchlist):
        result = watchlist.get_my_watchlist(
            current_user=mock_current_user,
            resources=mock_resources,
        )

        assert len(result) == 1
        assert result[0].user_id == "user123"
        assert result[0].movie_id == 1
        assert result[0].added_at == sample_watchlist_item.added_at


def test_get_my_watchlist_empty(mock_resources, mock_current_user):
    with patch("app.routers.watchlist.watchlist_service.get_user_watchlist", return_value=[]):
        result = watchlist.get_my_watchlist(
            current_user=mock_current_user,
            resources=mock_resources,
        )

        assert len(result) == 0


def test_add_to_watchlist_success(mock_resources, mock_current_user, sample_watchlist_item):
    item_data = WatchlistItemCreate(movie_id=1)

    with patch("app.routers.watchlist.watchlist_service.add_to_watchlist", return_value=sample_watchlist_item):
        result = watchlist.add_to_watchlist(
            item=item_data,
            current_user=mock_current_user,
            resources=mock_resources,
        )

        assert result.movie_id == 1
        assert result.user_id == "user123"
        assert result.added_at is not None


def test_add_to_watchlist_movie_not_found(mock_resources, mock_current_user):
    item_data = WatchlistItemCreate(movie_id=999)

    with patch("app.routers.watchlist.watchlist_service.add_to_watchlist", side_effect=ValueError("Movie not found")):
        with pytest.raises(HTTPException) as exc_info:
            watchlist.add_to_watchlist(
                item=item_data,
                current_user=mock_current_user,
                resources=mock_resources,
            )

        assert exc_info.value.status_code == 400


def test_add_to_watchlist_already_exists(mock_resources, mock_current_user):
    item_data = WatchlistItemCreate(movie_id=1)

    with patch(
        "app.routers.watchlist.watchlist_service.add_to_watchlist",
        side_effect=ValueError("Already in watchlist"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            watchlist.add_to_watchlist(
                item=item_data,
                current_user=mock_current_user,
                resources=mock_resources,
            )

        assert exc_info.value.status_code == 400


def test_remove_from_watchlist_success(mock_resources, mock_current_user):
    with patch("app.routers.watchlist.watchlist_service.remove_from_watchlist", return_value=True):
        result = watchlist.remove_from_watchlist(
            movie_id=1,
            current_user=mock_current_user,
            resources=mock_resources,
        )

        assert result is None


def test_remove_from_watchlist_not_found(mock_resources, mock_current_user):
    with patch("app.routers.watchlist.watchlist_service.remove_from_watchlist", return_value=False):
        result = watchlist.remove_from_watchlist(
            movie_id=999,
            current_user=mock_current_user,
            resources=mock_resources,
        )

        assert result is None


def test_remove_from_watchlist_error(mock_resources, mock_current_user):
    with patch(
        "app.routers.watchlist.watchlist_service.remove_from_watchlist",
        side_effect=Exception("Database error"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            watchlist.remove_from_watchlist(
                movie_id=1,
                current_user=mock_current_user,
                resources=mock_resources,
            )

        assert exc_info.value.status_code == 400


def test_check_in_watchlist_true(mock_resources, mock_current_user):
    with patch("app.routers.watchlist.watchlist_service.is_in_watchlist", return_value=True):
        result = watchlist.check_in_watchlist(
            movie_id=1,
            current_user=mock_current_user,
            resources=mock_resources,
        )

        assert result is True


def test_check_in_watchlist_false(mock_resources, mock_current_user):
    with patch("app.routers.watchlist.watchlist_service.is_in_watchlist", return_value=False):
        result = watchlist.check_in_watchlist(
            movie_id=999,
            current_user=mock_current_user,
            resources=mock_resources,
        )

        assert result is False


def test_check_in_watchlist_error(mock_resources, mock_current_user):
    with patch("app.routers.watchlist.watchlist_service.is_in_watchlist", side_effect=Exception("Database error")):
        with pytest.raises(HTTPException) as exc_info:
            watchlist.check_in_watchlist(
                movie_id=1,
                current_user=mock_current_user,
                resources=mock_resources,
            )

        assert exc_info.value.status_code == 400
