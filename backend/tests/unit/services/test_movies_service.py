"""Unit tests for movies service."""

from unittest.mock import Mock

import pandas as pd
import pytest

from app.services import movies_service


@pytest.fixture
def mock_resources():
    resources = Mock()
    resources.movies_repo = Mock()
    return resources


@pytest.fixture
def sample_movies():
    return [
        {
            "movie_id": 1,
            "title": "Toy Story (1995)",
            "genres": ["Animation", "Children", "Comedy"],
            "year": 1995,
        },
        {
            "movie_id": 2,
            "title": "Are People Actually Reading These Titles? (2025)",
            "genres": ["Adventure", "Comedy", "Fantasy"],
            "year": 2025,
        },
        {
            "movie_id": 3,
            "title": "2001: A Space Odyssey (1968)",
            "genres": ["Sci-Fi", "Adventure", "Mystery"],
            "year": 1968,
        },
    ]


def test_get_movies_with_pagination(mock_resources, sample_movies):
    mock_resources.movies_repo.get_all.return_value = sample_movies
    mock_resources.movies_repo.movies_df = pd.DataFrame(sample_movies)
    mock_resources.movies_repo.get_average_rating.return_value = 4.5

    result = movies_service.get_movies(mock_resources, page=1, page_size=30)

    assert result.page == 1
    assert result.page_size == 30
    assert result.total == 3
    assert result.total_pages == 1
    assert len(result.movies) == 3
    assert result.movies[0].movie_id == 1


def test_get_movies_calculates_total_pages(mock_resources, sample_movies):
    mock_resources.movies_repo.get_all.return_value = sample_movies[:2]
    mock_resources.movies_repo.movies_df = pd.DataFrame(sample_movies * 10)  # 30 movies
    mock_resources.movies_repo.get_average_rating.return_value = 4.0

    result = movies_service.get_movies(mock_resources, page=1, page_size=10)

    assert result.total == 30
    assert result.total_pages == 3


def test_get_movies_adds_average_ratings(mock_resources, sample_movies):
    mock_resources.movies_repo.get_all.return_value = sample_movies
    mock_resources.movies_repo.movies_df = pd.DataFrame(sample_movies)

    def mock_get_rating(movie_id):
        return 4.5 if movie_id == 1 else 3.0

    mock_resources.movies_repo.get_average_rating.side_effect = mock_get_rating

    result = movies_service.get_movies(mock_resources, page=1, page_size=30)

    assert result.movies[0].average_rating == 4.5
    assert result.movies[1].average_rating == 3.0


def test_get_movie_by_id_success(mock_resources):
    movie_data = {
        "movie_id": 1,
        "title": "Toy Story (1995)",
        "genres": ["Animation", "Children", "Comedy"],
    }
    mock_resources.movies_repo.get_by_id.return_value = movie_data
    mock_resources.movies_repo.get_average_rating.return_value = 4.5

    result = movies_service.get_movie_by_id(mock_resources, 1)

    assert result is not None
    assert result.movie_id == 1
    assert result.title == "Toy Story (1995)"
    assert result.average_rating == 4.5


def test_get_movie_by_id_not_found(mock_resources):
    mock_resources.movies_repo.get_by_id.return_value = None

    result = movies_service.get_movie_by_id(mock_resources, 999)

    assert result is None


def test_get_movie_by_id_invalid_id(mock_resources):
    result = movies_service.get_movie_by_id(mock_resources, -42)

    assert result is None
    mock_resources.movies_repo.get_by_id.assert_not_called()


def test_search_movies(mock_resources, sample_movies):
    mock_resources.movies_repo.search.return_value = [sample_movies[0]]
    mock_resources.movies_repo.get_average_rating.return_value = 4.5

    result = movies_service.search_movies(mock_resources, "Toy Story", limit=20)

    assert len(result) == 1
    assert result[0].title == "Toy Story (1995)"
    mock_resources.movies_repo.search.assert_called_once_with(query="Toy Story", limit=20)


def test_search_movies_adds_ratings(mock_resources, sample_movies):
    mock_resources.movies_repo.search.return_value = sample_movies[:2]
    mock_resources.movies_repo.get_average_rating.return_value = 4.2

    result = movies_service.search_movies(mock_resources, "1995")

    assert all(movie.average_rating == 4.2 for movie in result)


def test_filter_movies_by_genre(mock_resources, sample_movies):
    comedy_movies = [m for m in sample_movies if "Comedy" in m["genres"]]
    mock_resources.movies_repo.filter_by_genre.return_value = comedy_movies
    mock_resources.movies_repo.get_average_rating.return_value = 4.0

    result = movies_service.filter_movies(mock_resources, genre="Comedy", limit=20)

    assert len(result) == 2
    assert all(movie.genres and "Comedy" in movie.genres for movie in result)
    mock_resources.movies_repo.filter_by_genre.assert_called_once_with(genre="Comedy", limit=20)


def test_filter_movies_without_genre(mock_resources, sample_movies):
    mock_resources.movies_repo.get_all.return_value = sample_movies
    mock_resources.movies_repo.get_average_rating.return_value = 4.0

    result = movies_service.filter_movies(mock_resources, genre=None, limit=20)

    assert len(result) == 3
    mock_resources.movies_repo.get_all.assert_called_once_with(limit=20)
    mock_resources.movies_repo.filter_by_genre.assert_not_called()


def test_get_all_genres(mock_resources):
    genres = ["Action", "Adventure", "Animation", "Comedy", "Drama"]
    mock_resources.movies_repo.get_genres.return_value = genres

    result = movies_service.get_all_genres(mock_resources)

    assert result == genres
    mock_resources.movies_repo.get_genres.assert_called_once()


def test_get_movie_ratings(mock_resources):
    ratings = [
        {"id": 1, "user_id": "u1", "movie_id": 1, "rating": 5.0},
        {"id": 2, "user_id": "u2", "movie_id": 1, "rating": 4.0},
    ]
    mock_resources.ratings_repo.get_by_movie.return_value = ratings

    result = movies_service.get_movie_ratings(mock_resources, 1)

    assert result == ratings
    mock_resources.ratings_repo.get_by_movie.assert_called_once_with(1)


def test_get_movies_empty_result(mock_resources):
    mock_resources.movies_repo.get_all.return_value = []
    mock_resources.movies_repo.movies_df = pd.DataFrame()

    result = movies_service.get_movies(mock_resources, page=1, page_size=30)

    assert result.total == 0
    assert result.total_pages == 1
    assert len(result.movies) == 0


def test_get_movies_with_different_page_sizes(mock_resources, sample_movies):
    mock_resources.movies_repo.get_all.return_value = sample_movies[:2]
    mock_resources.movies_repo.movies_df = pd.DataFrame(sample_movies * 20)  # 60 movies
    mock_resources.movies_repo.get_average_rating.return_value = 4.0

    result = movies_service.get_movies(mock_resources, page=2, page_size=20)

    assert result.page == 2
    assert result.page_size == 20
    assert result.total_pages == 3
    mock_resources.movies_repo.get_all.assert_called_once_with(limit=20, offset=20)
