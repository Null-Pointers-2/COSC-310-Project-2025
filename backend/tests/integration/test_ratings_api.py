"""
Integration tests for ratings API endpoints.
"""

from datetime import UTC, datetime, timezone
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from app.routers import ratings
from app.schemas.rating import Rating, RatingCreate, RatingUpdate


@pytest.fixture
def mock_resources():
    return Mock()


@pytest.fixture
def mock_current_user():
    return {"id": "user123", "username": "testuser", "role": "user"}


@pytest.fixture
def sample_rating():
    return Rating(
        id=1,
        user_id="user123",
        movie_id=1,
        rating=4.5,
        timestamp=datetime.now(UTC),
    )


def test_create_rating_success(mock_resources, mock_current_user, sample_rating):
    rating_data = RatingCreate(movie_id=1, rating=4.5)

    with patch("app.routers.ratings.ratings_service.create_rating", return_value=sample_rating):
        result = ratings.create_rating(
            rating_data=rating_data,
            current_user=mock_current_user,
            resources=mock_resources,
        )

        assert result.id == 1
        assert result.rating == 4.5
        assert result.user_id == "user123"


def test_create_rating_duplicate(mock_resources, mock_current_user):
    rating_data = RatingCreate(movie_id=1, rating=4.5)

    with patch("app.routers.ratings.ratings_service.create_rating", side_effect=ValueError("Rating already exists")):
        with pytest.raises(HTTPException) as exc_info:
            ratings.create_rating(
                rating_data=rating_data,
                current_user=mock_current_user,
                resources=mock_resources,
            )

        assert exc_info.value.status_code == 400
        assert "already exists" in str(exc_info.value.detail).lower()


def test_get_my_ratings(mock_resources, mock_current_user, sample_rating):
    mock_ratings = [sample_rating]

    with patch("app.routers.ratings.ratings_service.get_user_ratings", return_value=mock_ratings):
        result = ratings.get_my_ratings(
            current_user=mock_current_user,
            resources=mock_resources,
        )

        assert len(result) == 1
        assert result[0].user_id == "user123"


def test_get_rating_by_id_success(mock_resources, sample_rating):
    with patch("app.routers.ratings.ratings_service.get_rating_by_id", return_value=sample_rating):
        result = ratings.get_rating(rating_id=1, resources=mock_resources)

        assert result.id == 1
        assert result.rating == 4.5


def test_get_rating_by_id_not_found(mock_resources):
    with patch("app.routers.ratings.ratings_service.get_rating_by_id", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            ratings.get_rating(rating_id=999, resources=mock_resources)

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()


def test_update_rating_success(mock_resources, mock_current_user, sample_rating):
    update_data = RatingUpdate(rating=5.0)
    updated_rating = Rating(
        id=1,
        user_id="user123",
        movie_id=1,
        rating=5.0,
        timestamp=datetime.now(UTC),
    )

    with (
        patch("app.routers.ratings.ratings_service.get_rating_by_id", return_value=sample_rating),
        patch("app.routers.ratings.ratings_service.update_rating", return_value=updated_rating),
    ):
        result = ratings.update_rating(
            rating_id=1,
            update_data=update_data,
            current_user=mock_current_user,
            resources=mock_resources,
        )

        assert result.rating == 5.0


def test_update_rating_not_found(mock_resources, mock_current_user):
    update_data = RatingUpdate(rating=5.0)

    with patch("app.routers.ratings.ratings_service.get_rating_by_id", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            ratings.update_rating(
                rating_id=999,
                update_data=update_data,
                current_user=mock_current_user,
                resources=mock_resources,
            )

        assert exc_info.value.status_code == 404


def test_update_rating_wrong_user(mock_resources, mock_current_user, sample_rating):
    wrong_user_rating = Rating(
        id=1,
        user_id="different_user",
        movie_id=1,
        rating=4.5,
        timestamp=datetime.now(UTC),
    )
    update_data = RatingUpdate(rating=5.0)

    with patch("app.routers.ratings.ratings_service.get_rating_by_id", return_value=wrong_user_rating):
        with pytest.raises(HTTPException) as exc_info:
            ratings.update_rating(
                rating_id=1,
                update_data=update_data,
                current_user=mock_current_user,
                resources=mock_resources,
            )

        assert exc_info.value.status_code == 403


def test_update_rating_fails(mock_resources, mock_current_user, sample_rating):
    update_data = RatingUpdate(rating=5.0)

    with (
        patch("app.routers.ratings.ratings_service.get_rating_by_id", return_value=sample_rating),
        patch("app.routers.ratings.ratings_service.update_rating", return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            ratings.update_rating(
                rating_id=1,
                update_data=update_data,
                current_user=mock_current_user,
                resources=mock_resources,
            )

        assert exc_info.value.status_code == 400


def test_delete_rating_success(mock_resources, mock_current_user, sample_rating):
    with (
        patch("app.routers.ratings.ratings_service.get_rating_by_id", return_value=sample_rating),
        patch("app.routers.ratings.ratings_service.delete_rating", return_value=True),
    ):
        ratings.delete_rating(
            rating_id=1,
            current_user=mock_current_user,
            resources=mock_resources,
        )


def test_delete_rating_not_found(mock_resources, mock_current_user):
    with patch("app.routers.ratings.ratings_service.get_rating_by_id", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            ratings.delete_rating(
                rating_id=999,
                current_user=mock_current_user,
                resources=mock_resources,
            )

        assert exc_info.value.status_code == 404


def test_delete_rating_wrong_user(mock_resources, mock_current_user):
    wrong_user_rating = Rating(
        id=1,
        user_id="different_user",
        movie_id=1,
        rating=4.5,
        timestamp=datetime.now(UTC),
    )

    with patch("app.routers.ratings.ratings_service.get_rating_by_id", return_value=wrong_user_rating):
        with pytest.raises(HTTPException) as exc_info:
            ratings.delete_rating(
                rating_id=1,
                current_user=mock_current_user,
                resources=mock_resources,
            )

        assert exc_info.value.status_code == 403


def test_delete_rating_fails(mock_resources, mock_current_user, sample_rating):
    with (
        patch("app.routers.ratings.ratings_service.get_rating_by_id", return_value=sample_rating),
        patch("app.routers.ratings.ratings_service.delete_rating", return_value=False),
    ):
        with pytest.raises(HTTPException) as exc_info:
            ratings.delete_rating(
                rating_id=1,
                current_user=mock_current_user,
                resources=mock_resources,
            )

        assert exc_info.value.status_code == 400
