"""
Integration tests for movies API endpoints.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from app.routers import movies
from app.schemas.movie import Movie, MoviePage


@pytest.fixture
def mock_resources():
    return Mock()


def test_get_movies_endpoint(mock_resources):
    mock_page = MoviePage(
        movies=[
            Movie(movie_id=1, title="Test Movie", genres=["Action"]),
            Movie(movie_id=2, title="Test Movie 2", genres=["Comedy"]),
        ],
        total=2,
        page=1,
        page_size=30,
        total_pages=1,
    )

    with patch("app.routers.movies.movies_service.get_movies", return_value=mock_page):
        result = movies.get_movies(page=1, page_size=30, resources=mock_resources)

        assert result.total == 2
        assert len(result.movies) == 2
        assert result.page == 1


def test_get_movies_with_custom_pagination(mock_resources):
    mock_page = MoviePage(
        movies=[Movie(movie_id=1, title="Test", genres=[])],
        total=100,
        page=3,
        page_size=10,
        total_pages=10,
    )

    with patch("app.routers.movies.movies_service.get_movies", return_value=mock_page):
        result = movies.get_movies(page=3, page_size=10, resources=mock_resources)

        assert result.page == 3
        assert result.page_size == 10
        assert result.total_pages == 10


def test_search_movies_via_get_movies(mock_resources):
    """Test searching via the main get_movies endpoint."""
    mock_page = MoviePage(
        movies=[
            Movie(movie_id=1, title="Matrix", genres=["Action", "Sci-Fi"]),
        ],
        total=1,
        page=1,
        page_size=20,
        total_pages=1,
    )

    with patch("app.routers.movies.movies_service.get_movies", return_value=mock_page) as mock_service:
        result = movies.get_movies(query="Matrix", page=1, page_size=20, resources=mock_resources)

        assert len(result.movies) == 1
        mock_service.assert_called_once_with(mock_resources, page=1, page_size=20, query="Matrix", genre=None)


def test_filter_movies_via_get_movies(mock_resources):
    """Test filtering via the main get_movies endpoint."""
    mock_page = MoviePage(
        movies=[
            Movie(movie_id=1, title="Action Movie 1", genres=["Action"]),
        ],
        total=1,
        page=1,
        page_size=20,
        total_pages=1,
    )

    with patch("app.routers.movies.movies_service.get_movies", return_value=mock_page) as mock_service:
        result = movies.get_movies(genre="Action", page=1, page_size=20, resources=mock_resources)

        assert len(result.movies) == 1
        mock_service.assert_called_once_with(mock_resources, page=1, page_size=20, query=None, genre="Action")


def test_get_genres_endpoint(mock_resources):
    mock_genres = ["Action", "Adventure", "Animation", "Comedy", "Drama"]

    with patch("app.routers.movies.movies_service.get_all_genres", return_value=mock_genres):
        result = movies.get_genres(resources=mock_resources)

        assert result == mock_genres
        assert len(result) == 5


def test_get_movie_by_id_success(mock_resources):
    mock_movie = Movie(movie_id=1, title="Test Movie", genres=["Action"], average_rating=4.5)

    with patch("app.routers.movies.movies_service.get_movie_by_id", return_value=mock_movie):
        result = movies.get_movie(movie_id=1, resources=mock_resources)

        assert result.movie_id == 1
        assert result.title == "Test Movie"
        assert result.average_rating == 4.5


def test_get_movie_by_id_not_found(mock_resources):
    with patch("app.routers.movies.movies_service.get_movie_by_id", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            movies.get_movie(movie_id=999, resources=mock_resources)

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()


def test_get_movie_ratings_success(mock_resources):
    mock_ratings = [
        {"id": 1, "user_id": "u1", "movie_id": 1, "rating": 5.0},
        {"id": 2, "user_id": "u2", "movie_id": 1, "rating": 4.0},
    ]

    with (
        patch("app.routers.movies.movies_service.get_movie_by_id") as mock_get_movie,
        patch("app.routers.movies.movies_service.get_movie_ratings", return_value=mock_ratings) as mock_get_ratings,
    ):
        mock_get_movie.return_value = Movie(movie_id=1, title="Test", genres=[])

        result = movies.get_movie_ratings(movie_id=1, resources=mock_resources)

        assert result == mock_ratings
        assert len(result) == 2


def test_get_movie_ratings_movie_not_found(mock_resources):
    with patch("app.routers.movies.movies_service.get_movie_by_id", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            movies.get_movie_ratings(movie_id=999, resources=mock_resources)

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()
