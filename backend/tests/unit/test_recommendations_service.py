"""Unit tests for recommendations service."""

from unittest.mock import MagicMock, Mock

import pytest

from app.schemas.recommendation import RecommendationItem
from app.services import recommendations_service


@pytest.fixture
def mock_resources():
    """Mock resources object with repositories."""
    resources = Mock()

    return resources


@pytest.fixture
def mock_recommender(mocker):
    mock_recommender_class = mocker.patch("app.services.recommendations_service.MovieRecommender", autospec=True)
    mock_instance = MagicMock()
    mock_recommender_class.return_value = mock_instance

    mocker.patch.object(recommendations_service, "_recommender", None)

    return mock_instance


def test_returns_cached_recommendations_when_fresh(mock_resources, mock_recommender):
    cached_data = {
        "recommendations": [
            {"movie_id": 100, "similarity_score": 0.95},
            {"movie_id": 101, "similarity_score": 0.90},
        ]
    }
    mock_resources.recommendations_repo.get_for_user.return_value = cached_data
    mock_resources.recommendations_repo.is_fresh.return_value = True

    result = recommendations_service.get_recommendations(mock_resources, "user123", limit=10)

    assert result.user_id == "user123"
    assert len(result.recommendations) == 2
    assert result.recommendations[0].movie_id == 100
    mock_recommender.get_recommendations.assert_not_called()
    mock_resources.recommendations_repo.get_for_user.assert_called_once_with("user123")
    mock_resources.recommendations_repo.is_fresh.assert_called_once()


def test_generates_new_recommendations_when_cache_stale(mocker, mock_resources, mock_recommender):
    mock_resources.recommendations_repo.get_for_user.return_value = None
    mock_resources.ratings_repo.get_by_user.return_value = [
        {"movie_id": 1, "rating": 4.5},
        {"movie_id": 2, "rating": 4.0},
    ]
    mock_resources.movies_repo.get_by_id.side_effect = lambda mid: {
        "movieId": mid,
        "title": f"Movie {mid}",
    }

    mock_generate = mocker.patch(
        "app.services.recommendations_service.generate_recommendations",
        return_value=[
            RecommendationItem(movie_id=100, similarity_score=0.95),
            RecommendationItem(movie_id=101, similarity_score=0.90),
        ],
    )

    result = recommendations_service.get_recommendations(mock_resources, "user123", limit=10)

    assert len(result.recommendations) == 2
    mock_generate.assert_called_once_with(mock_resources, "user123", 10)
    mock_resources.recommendations_repo.save_for_user.assert_called_once()


def test_force_refresh_bypasses_cache(mocker, mock_resources):
    mock_generate = mocker.patch(
        "app.services.recommendations_service.generate_recommendations",
        return_value=[RecommendationItem(movie_id=200, similarity_score=0.88)],
    )

    result = recommendations_service.get_recommendations(mock_resources, "user123", limit=10, force_refresh=True)

    assert len(result.recommendations) == 1
    mock_resources.recommendations_repo.get_for_user.assert_not_called()
    mock_generate.assert_called_once_with(mock_resources, "user123", 10)


def test_returns_fallback_for_user_with_no_ratings(mock_resources, mock_recommender):
    mock_resources.ratings_repo.get_by_user.return_value = []
    mock_resources.movies_repo.get_all.return_value = [
        {"movieId": 1, "title": "Movie 1"},
        {"movieId": 2, "title": "Movie 2"},
    ]

    result = recommendations_service.generate_recommendations(mock_resources, "user123", limit=10)

    assert len(result) == 2
    assert result[0].similarity_score == 0.5
    mock_resources.movies_repo.get_all.assert_called_once_with(limit=10)


def test_uses_high_rated_movies_as_seeds(mocker, mock_resources, mock_recommender):
    mock_resources.ratings_repo.get_by_user.return_value = [
        {"movie_id": 1, "rating": 4.5},
        {"movie_id": 2, "rating": 4.0},
        {"movie_id": 3, "rating": 3.0},
        {"movie_id": 4, "rating": 5.0},
    ]
    mock_resources.movies_repo.get_by_id.side_effect = lambda mid: {
        "movieId": mid,
        "title": f"Movie {mid}",
    }

    mock_get_similar = mocker.patch(
        "app.services.recommendations_service.get_similar_movies",
        return_value=[RecommendationItem(movie_id=100, similarity_score=0.9)],
    )

    recommendations_service.generate_recommendations(mock_resources, "user123", limit=10)

    seed_movie_ids = [call.args[1] for call in mock_get_similar.call_args_list]  # Second arg is movie_id
    assert 1 in seed_movie_ids and 2 in seed_movie_ids and 4 in seed_movie_ids
    assert 3 not in seed_movie_ids


def test_excludes_already_rated_movies(mocker, mock_resources, mock_recommender):
    mock_resources.ratings_repo.get_by_user.return_value = [
        {"movie_id": 1, "rating": 4.5},
        {"movie_id": 2, "rating": 4.0},
    ]
    mock_resources.movies_repo.get_by_id.return_value = {
        "movieId": 1,
        "title": "Movie 1",
    }

    mocker.patch(
        "app.services.recommendations_service.get_similar_movies",
        return_value=[
            RecommendationItem(movie_id=2, similarity_score=0.95),
            RecommendationItem(movie_id=100, similarity_score=0.90),
        ],
    )

    result = recommendations_service.generate_recommendations(mock_resources, "user123", limit=10)
    movie_ids = [r.movie_id for r in result]
    assert 2 not in movie_ids and 100 in movie_ids


def test_aggregates_scores_from_multiple_seeds(mocker, mock_resources, mock_recommender):
    mock_resources.ratings_repo.get_by_user.return_value = [
        {"movie_id": 1, "rating": 4.0},
        {"movie_id": 2, "rating": 5.0},
    ]
    mock_resources.movies_repo.get_by_id.side_effect = lambda mid: {
        "movieId": mid,
        "title": f"Movie {mid}",
    }

    def mock_similar(resources, movie_id, limit):
        if movie_id == 1:
            return [RecommendationItem(movie_id=100, similarity_score=0.8)]
        if movie_id == 2:
            return [RecommendationItem(movie_id=100, similarity_score=0.9)]
        return []

    mocker.patch(
        "app.services.recommendations_service.get_similar_movies",
        side_effect=mock_similar,
    )

    result = recommendations_service.generate_recommendations(mock_resources, "user123", limit=10)
    movie_100 = next(r for r in result if r.movie_id == 100)
    assert 0.7 < movie_100.similarity_score < 0.9


def test_returns_similar_movies_for_valid_movie(mocker, mock_resources, mock_recommender):
    def mock_get_by_id(movie_id):
        if movie_id == 1:
            return {"movieId": 1, "title": "The Matrix (1999)"}
        if movie_id == 2:
            return {"movieId": 2, "title": "The Matrix Reloaded (2003)"}
        if movie_id == 3:
            return {"movieId": 3, "title": "Inception (2010)"}
        return None

    mock_resources.movies_repo.get_by_id.side_effect = mock_get_by_id

    mock_recommender.get_similar_by_id.return_value = [
        (2, 0.92),
        (3, 0.88),
    ]

    result = recommendations_service.get_similar_movies(mock_resources, 1, limit=2)
    assert len(result) == 2
    assert all(isinstance(r, RecommendationItem) for r in result)

    mock_recommender.get_similar_by_id.assert_called_once_with(1, n=2)

    assert result[0].movie_id == 2
    assert result[0].similarity_score == 0.92
    assert result[1].movie_id == 3
    assert result[1].similarity_score == 0.88

    assert mock_resources.movies_repo.get_by_id.call_count == 3


def test_returns_empty_for_invalid_movie(mock_resources, mock_recommender):
    mock_resources.movies_repo.get_by_id.return_value = None
    result = recommendations_service.get_similar_movies(mock_resources, 9999, limit=5)
    assert result == []
    mock_recommender.get_recommendations.assert_not_called()


def test_recommender_singleton(mocker):
    mock_recommender_class = mocker.patch("app.services.recommendations_service.MovieRecommender")
    mock_instance = MagicMock()
    mock_recommender_class.return_value = mock_instance

    recommendations_service._recommender = None
    r1 = recommendations_service._get_recommender()
    r2 = recommendations_service._get_recommender()

    assert r1 is r2
    assert mock_recommender_class.call_count == 1


def test_clear_cache_calls_repo(mock_resources):
    recommendations_service.clear_recommendations_cache(mock_resources, "user123")
    mock_resources.recommendations_repo.clear_for_user.assert_called_once_with("user123")


def test_fallback_respects_limit(mock_resources):
    def get_all_mock(limit=None):
        actual_limit = limit or 0
        return [{"movieId": i, "title": f"Movie {i}"} for i in range(actual_limit)]

    mock_resources.movies_repo.get_all.side_effect = get_all_mock

    result = recommendations_service._get_fallback_recommendations(mock_resources, limit=5)
    assert len(result) == 5
    mock_resources.movies_repo.get_all.assert_called_once_with(limit=5)


def test_refresh_calls_get_with_force_refresh(mocker, mock_resources):
    mock_get = mocker.patch(
        "app.services.recommendations_service.get_recommendations",
        return_value=Mock(user_id="user123", recommendations=[]),
    )

    recommendations_service.refresh_recommendations_for_user(mock_resources, "user123", limit=10)

    mock_get.assert_called_once_with(mock_resources, "user123", limit=10, force_refresh=True)
