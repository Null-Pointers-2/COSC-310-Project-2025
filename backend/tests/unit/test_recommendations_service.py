"""Unit tests for recommendations_service."""
import pytest
from unittest.mock import MagicMock
from app.services import recommendations_service
from app.schemas.recommendation import RecommendationItem


@pytest.fixture
def mock_repos(mocker):
    """Mock repository dependencies inside recommendations_service."""
    mock_ratings = mocker.patch("app.services.recommendations_service.ratings_repo", autospec=True)
    mock_recommendations = mocker.patch("app.services.recommendations_service.recommendations_repo", autospec=True)
    mock_movies = mocker.patch("app.services.recommendations_service.movies_repo", autospec=True)

    mock_recommendations.get_for_user = MagicMock()
    mock_recommendations.is_fresh = MagicMock()
    mock_recommendations.save_for_user = MagicMock()
    mock_recommendations.clear_for_user = MagicMock()
    mock_ratings.get_by_user = MagicMock()
    mock_movies.get_by_id = MagicMock()
    mock_movies.search = MagicMock()
    mock_movies.get_all = MagicMock()

    return {
        "ratings": mock_ratings,
        "recommendations": mock_recommendations,
        "movies": mock_movies,
    }


@pytest.fixture
def mock_recommender(mocker):
    """Mock the singleton MovieRecommender."""
    mock_recommender_class = mocker.patch("app.services.recommendations_service.MovieRecommender", autospec=True)
    mock_instance = MagicMock()
    mock_recommender_class.return_value = mock_instance
    mocker.patch.object(recommendations_service, "_recommender", None)
    return mock_instance

def test_returns_cached_recommendations_when_fresh(mock_repos, mock_recommender):
    """Should return cached recommendations if cache is fresh."""
    cached_data = {
        "recommendations": [
            {"movie_id": 100, "similarity_score": 0.95},
            {"movie_id": 101, "similarity_score": 0.90},
        ]
    }
    mock_repos["recommendations"].get_for_user.return_value = cached_data
    mock_repos["recommendations"].is_fresh.return_value = True

    result = recommendations_service.get_recommendations("user123", limit=10)

    assert result.user_id == "user123"
    assert len(result.recommendations) == 2
    assert result.recommendations[0].movie_id == 100
    mock_recommender.get_recommendations.assert_not_called()
    mock_repos["recommendations"].get_for_user.assert_called_once_with("user123")
    mock_repos["recommendations"].is_fresh.assert_called_once()


def test_generates_new_recommendations_when_cache_stale(mocker, mock_repos, mock_recommender):
    """Should generate new recommendations if cache is stale or missing."""
    mock_repos["recommendations"].get_for_user.return_value = None
    mock_repos["ratings"].get_by_user.return_value = [
        {"movie_id": 1, "rating": 4.5},
        {"movie_id": 2, "rating": 4.0},
    ]
    mock_repos["movies"].get_by_id.side_effect = lambda mid: {"movieId": mid, "title": f"Movie {mid}"}

    mock_generate = mocker.patch(
        "app.services.recommendations_service.generate_recommendations",
        return_value=[
            RecommendationItem(movie_id=100, similarity_score=0.95),
            RecommendationItem(movie_id=101, similarity_score=0.90),
        ],
    )

    result = recommendations_service.get_recommendations("user123", limit=10)

    assert len(result.recommendations) == 2
    mock_generate.assert_called_once_with("user123", 10)
    mock_repos["recommendations"].save_for_user.assert_called_once()


def test_force_refresh_bypasses_cache(mocker, mock_repos):
    """Should bypass cache when force_refresh=True."""
    mock_generate = mocker.patch(
        "app.services.recommendations_service.generate_recommendations",
        return_value=[RecommendationItem(movie_id=200, similarity_score=0.88)],
    )

    result = recommendations_service.get_recommendations("user123", limit=10, force_refresh=True)

    assert len(result.recommendations) == 1
    mock_repos["recommendations"].get_for_user.assert_not_called()
    mock_generate.assert_called_once_with("user123", 10)


def test_returns_fallback_for_user_with_no_ratings(mock_repos):
    """Should return fallback recommendations for new users."""
    mock_repos["ratings"].get_by_user.return_value = []
    mock_repos["movies"].get_all.return_value = [
        {"movieId": 1, "title": "Movie 1"},
        {"movieId": 2, "title": "Movie 2"},
    ]

    result = recommendations_service.generate_recommendations("user123", limit=10)

    assert len(result) == 2
    assert result[0].similarity_score == 0.5
    mock_repos["movies"].get_all.assert_called_once_with(limit=10)


def test_uses_high_rated_movies_as_seeds(mocker, mock_repos):
    """Should use only ratings >= 4.0 as seeds."""
    mock_repos["ratings"].get_by_user.return_value = [
        {"movie_id": 1, "rating": 4.5},
        {"movie_id": 2, "rating": 4.0},
        {"movie_id": 3, "rating": 3.0},
        {"movie_id": 4, "rating": 5.0},
    ]
    mock_repos["movies"].get_by_id.side_effect = lambda mid: {"movieId": mid, "title": f"Movie {mid}"}

    mock_get_similar = mocker.patch(
        "app.services.recommendations_service.get_similar_movies",
        return_value=[RecommendationItem(movie_id=100, similarity_score=0.9)],
    )

    recommendations_service.generate_recommendations("user123", limit=10)

    seed_movie_ids = [call.args[0] for call in mock_get_similar.call_args_list]
    assert 1 in seed_movie_ids and 2 in seed_movie_ids and 4 in seed_movie_ids
    assert 3 not in seed_movie_ids


def test_excludes_already_rated_movies(mocker, mock_repos):
    """Should exclude movies the user already rated."""
    mock_repos["ratings"].get_by_user.return_value = [
        {"movie_id": 1, "rating": 4.5},
        {"movie_id": 2, "rating": 4.0},
    ]
    mock_repos["movies"].get_by_id.return_value = {"movieId": 1, "title": "Movie 1"}

    mocker.patch(
        "app.services.recommendations_service.get_similar_movies",
        return_value=[
            RecommendationItem(movie_id=2, similarity_score=0.95),
            RecommendationItem(movie_id=100, similarity_score=0.90),
        ],
    )

    result = recommendations_service.generate_recommendations("user123", limit=10)
    movie_ids = [r.movie_id for r in result]
    assert 2 not in movie_ids and 100 in movie_ids


def test_aggregates_scores_from_multiple_seeds(mocker, mock_repos):
    """Should combine scores from multiple seed movies."""
    mock_repos["ratings"].get_by_user.return_value = [
        {"movie_id": 1, "rating": 4.0},
        {"movie_id": 2, "rating": 5.0},
    ]
    mock_repos["movies"].get_by_id.side_effect = lambda mid: {"movieId": mid, "title": f"Movie {mid}"}

    def mock_similar(movie_id, limit):
        if movie_id == 1:
            return [RecommendationItem(movie_id=100, similarity_score=0.8)]
        if movie_id == 2:
            return [RecommendationItem(movie_id=100, similarity_score=0.9)]
        return []

    mocker.patch("app.services.recommendations_service.get_similar_movies", side_effect=mock_similar)

    result = recommendations_service.generate_recommendations("user123", limit=10)
    movie_100 = next(r for r in result if r.movie_id == 100)
    assert 0.7 < movie_100.similarity_score < 0.9


def test_returns_similar_movies_for_valid_movie(mocker, mock_repos, mock_recommender):
    """Should return similar movies using recommender results."""
    mock_repos["movies"].get_by_id.return_value = {"movieId": 1, "title": "The Matrix (1999)"}
    mock_recommender.get_recommendations.return_value = [
        ("The Matrix Reloaded (2003)", 0.92),
        ("Inception (2010)", 0.88),
    ]
    mock_repos["movies"].search.side_effect = lambda t, limit: [{"movieId": 2, "title": t}]

    result = recommendations_service.get_similar_movies(1, limit=2)
    assert len(result) == 2
    assert all(isinstance(r, RecommendationItem) for r in result)
    mock_recommender.get_recommendations.assert_called_once()


def test_returns_empty_for_invalid_movie(mock_repos, mock_recommender):
    """Should return empty list for invalid movie."""
    mock_repos["movies"].get_by_id.return_value = None
    result = recommendations_service.get_similar_movies(9999, limit=5)
    assert result == []
    mock_recommender.get_recommendations.assert_not_called()


def test_recommender_singleton(mocker):
    """Should only initialize recommender once."""
    mock_recommender_class = mocker.patch("app.services.recommendations_service.MovieRecommender")
    mock_instance = MagicMock()
    mock_recommender_class.return_value = mock_instance

    recommendations_service._recommender = None
    r1 = recommendations_service._get_recommender()
    r2 = recommendations_service._get_recommender()

    assert r1 is r2
    assert mock_recommender_class.call_count == 1


def test_clear_cache_calls_repo(mock_repos):
    """Should delegate cache clearing to repository."""
    recommendations_service.clear_recommendations_cache("user123")
    mock_repos["recommendations"].clear_for_user.assert_called_once_with("user123")


def test_fallback_respects_limit(mock_repos):
    """Should respect limit parameter for fallback."""
    mock_repos["movies"].get_all.side_effect = lambda limit=None: [
        {"movieId": i, "title": f"Movie {i}"} for i in range(limit)
    ]
    result = recommendations_service._get_fallback_recommendations(limit=5)
    assert len(result) == 5
    mock_repos["movies"].get_all.assert_called_once_with(limit=5)