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


def test_get_movies_with_custom_pagination():
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


def test_search_movies_endpoint():
    mock_movies = [
        Movie(movie_id=1, title="Matrix", genres=["Action", "Sci-Fi"]),
        Movie(movie_id=2, title="Matrix Reloaded", genres=["Action", "Sci-Fi"]),
    ]

    with patch("app.routers.movies.movies_service.search_movies", return_value=mock_movies):
        result = movies.search_movies(query="Matrix", limit=20, resources=mock_resources)

        assert len(result) == 2
        assert all("Matrix" in movie.title for movie in result)


def test_search_movies_with_limit():
    mock_movies = [Movie(movie_id=i, title=f"Movie {i}", genres=[]) for i in range(5)]

    with patch("app.routers.movies.movies_service.search_movies", return_value=mock_movies) as mock_search:
        movies.search_movies(query="test", limit=5, resources=mock_resources)

        mock_search.assert_called_once_with(mock_resources, query="test", limit=5)


def test_filter_movies_endpoint():
    mock_movies = [
        Movie(movie_id=1, title="Action Movie 1", genres=["Action"]),
        Movie(movie_id=2, title="Action Movie 2", genres=["Action"]),
    ]

    with patch("app.routers.movies.movies_service.filter_movies", return_value=mock_movies):
        result = movies.filter_movies(genre="Action", limit=20, resources=mock_resources)

        assert len(result) == 2
        assert all(movie.genres and "Action" in movie.genres for movie in result)


def test_filter_movies_without_genre():
    mock_movies = [Movie(movie_id=i, title=f"Movie {i}", genres=[]) for i in range(3)]

    with patch("app.routers.movies.movies_service.filter_movies", return_value=mock_movies) as mock_filter:
        result = movies.filter_movies(genre=None, limit=20, resources=mock_resources)

        assert len(result) == 3
        mock_filter.assert_called_once_with(mock_resources, genre=None, limit=20)


def test_get_genres_endpoint():
    mock_genres = ["Action", "Adventure", "Animation", "Comedy", "Drama"]

    with patch("app.routers.movies.movies_service.get_all_genres", return_value=mock_genres):
        result = movies.get_genres(resources=mock_resources)

        assert result == mock_genres
        assert len(result) == 5


def test_get_movie_by_id_success():
    mock_movie = Movie(movie_id=1, title="Test Movie", genres=["Action"], average_rating=4.5)

    with patch("app.routers.movies.movies_service.get_movie_by_id", return_value=mock_movie):
        result = movies.get_movie(movie_id=1, resources=mock_resources)

        assert result.movie_id == 1
        assert result.title == "Test Movie"
        assert result.average_rating == 4.5


def test_get_movie_by_id_not_found():
    with patch("app.routers.movies.movies_service.get_movie_by_id", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            movies.get_movie(movie_id=999, resources=mock_resources)

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()


def test_get_movie_ratings_success():
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


def test_get_movie_ratings_movie_not_found():
    with patch("app.routers.movies.movies_service.get_movie_by_id", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            movies.get_movie_ratings(movie_id=999, resources=mock_resources)

        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()
