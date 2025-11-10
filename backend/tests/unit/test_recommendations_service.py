"""Unit tests for recommendations service."""
import pytest
from unittest.mock import MagicMock
from app.services import recommendations_service
from app.schemas.recommendation import RecommendationItem


@pytest.fixture
def mock_repos(mocker):
    """Mock all repository dependencies."""
    mock_ratings_repo = mocker.patch("app.services.recommendations_service.ratings_repo")
    mock_recommendations_repo = mocker.patch("app.services.recommendations_service.recommendations_repo")
    mock_movies_repo = mocker.patch("app.services.recommendations_service.movies_repo")
    
    return {
        "ratings": mock_ratings_repo,
        "recommendations": mock_recommendations_repo,
        "movies": mock_movies_repo
    }


@pytest.fixture
def mock_recommender(mocker):
    """Mock the MovieRecommender."""
    mock = mocker.patch("app.services.recommendations_service._get_recommender")
    return mock

def test_returns_cached_recommendations_when_fresh(mock_repos, mock_recommender):
    """Test that cached recommendations are returned when fresh."""
    cached_data = {
        "recommendations": [
            {"movie_id": 100, "similarity_score": 0.95},
            {"movie_id": 101, "similarity_score": 0.90}
        ]
    }
    mock_repos["recommendations"].get_for_user.return_value = cached_data
    mock_repos["recommendations"].is_fresh.return_value = True
    
    result = recommendations_service.get_recommendations("user123", limit=10)
    
    assert result.user_id == "user123"
    assert len(result.recommendations) == 2
    assert result.recommendations[0].movie_id == 100
    assert result.recommendations[0].similarity_score == 0.95
    
    mock_recommender.assert_not_called()
    mock_repos["recommendations"].get_for_user.assert_called_once_with("user123")
    mock_repos["recommendations"].is_fresh.assert_called_once()

def test_generates_new_recommendations_when_cache_stale(self, mocker, mock_repos, mock_recommender):
    """Test that new recommendations are generated when cache is stale."""
    mock_repos["recommendations"].get_for_user.return_value = None
    mock_repos["ratings"].get_by_user.return_value = [
        {"movie_id": 1, "rating": 4.5},
        {"movie_id": 2, "rating": 4.0}
    ]
    mock_repos["movies"].get_by_id.side_effect = lambda mid: {"movieId": mid, "title": f"Movie {mid}"}
    
    mock_recommender_instance = MagicMock()
    mock_recommender_instance.get_recommendations.return_value = [
        ("Movie 100", 0.95),
        ("Movie 101", 0.90)
    ]
    mock_recommender.return_value = mock_recommender_instance
    
    def mock_search(title, limit):
        movie_id = int(title.split()[1])
        return [{"movieId": movie_id, "title": title}]
    
    mock_repos["movies"].search.side_effect = mock_search
    
    mock_generate = mocker.patch(
        "app.services.recommendations_service.generate_recommendations",
        return_value=[
            RecommendationItem(movie_id=100, similarity_score=0.95),
            RecommendationItem(movie_id=101, similarity_score=0.90)
        ]
    )
    
    result = recommendations_service.get_recommendations("user123", limit=10)
    
    assert result.user_id == "user123"
    assert len(result.recommendations) == 2
    mock_generate.assert_called_once_with("user123", 10)
    mock_repos["recommendations"].save_for_user.assert_called_once()

def test_force_refresh_regenerates_recommendations(self, mocker, mock_repos):
    """Test that force_refresh=True bypasses cache."""
    mock_generate = mocker.patch(
        "app.services.recommendations_service.generate_recommendations",
        return_value=[
            RecommendationItem(movie_id=200, similarity_score=0.88)
        ]
    )
    
    result = recommendations_service.get_recommendations("user123", limit=10, force_refresh=True)
    
    assert result.user_id == "user123"
    assert len(result.recommendations) == 1
    
    mock_repos["recommendations"].get_for_user.assert_not_called()
    mock_repos["recommendations"].is_fresh.assert_not_called()
    
    mock_generate.assert_called_once_with("user123", 10)
    mock_repos["recommendations"].save_for_user.assert_called_once()

def test_returns_fallback_for_user_with_no_ratings(self, mocker, mock_repos):
    """Test that fallback recommendations are returned for users with no ratings."""
    mock_repos["ratings"].get_by_user.return_value = []
    mock_repos["movies"].get_all.return_value = [
        {"movieId": 1, "title": "Movie 1"},
        {"movieId": 2, "title": "Movie 2"}
    ]
    
    result = recommendations_service.generate_recommendations("user123", limit=10)
    
    assert len(result) == 2
    assert result[0].movie_id == 1
    assert result[0].similarity_score == 0.5  # Default fallback score
    mock_repos["ratings"].get_by_user.assert_called_once_with("user123")

def test_uses_high_rated_movies_as_seeds(self, mocker, mock_repos, mock_recommender):
    """Test that movies rated >= 4.0 are used as seed movies."""
    mock_repos["ratings"].get_by_user.return_value = [
        {"movie_id": 1, "rating": 4.5},
        {"movie_id": 2, "rating": 4.0},
        {"movie_id": 3, "rating": 3.0},  # Below threshold
        {"movie_id": 4, "rating": 5.0}
    ]
    mock_repos["movies"].get_by_id.side_effect = lambda mid: {"movieId": mid, "title": f"Movie {mid}"}
    
    mock_get_similar = mocker.patch(
        "app.services.recommendations_service.get_similar_movies",
        return_value=[RecommendationItem(movie_id=100, similarity_score=0.9)]
    )
    
    result = recommendations_service.generate_recommendations("user123", limit=10)
    
    assert mock_get_similar.call_count >= 1
    
    seed_calls = [call[0][0] for call in mock_get_similar.call_args_list]
    assert 1 in seed_calls  # rating 4.5
    assert 2 in seed_calls  # rating 4.0
    assert 4 in seed_calls  # rating 5.0
    assert 3 not in seed_calls  # rating 3.0 (below threshold)

def test_excludes_already_rated_movies(self, mocker, mock_repos):
    """Test that already-rated movies are excluded from recommendations."""
    mock_repos["ratings"].get_by_user.return_value = [
        {"movie_id": 1, "rating": 4.5},
        {"movie_id": 2, "rating": 4.0},
        {"movie_id": 3, "rating": 3.5}
    ]
    mock_repos["movies"].get_by_id.side_effect = lambda mid: {"movieId": mid, "title": f"Movie {mid}"}
    
    mock_get_similar = mocker.patch(
        "app.services.recommendations_service.get_similar_movies",
        return_value=[
            RecommendationItem(movie_id=2, similarity_score=0.95),  # Already rated
            RecommendationItem(movie_id=100, similarity_score=0.90),  # New
            RecommendationItem(movie_id=3, similarity_score=0.85),  # Already rated
            RecommendationItem(movie_id=101, similarity_score=0.80)  # New
        ]
    )
    
    result = recommendations_service.generate_recommendations("user123", limit=10)
    
    recommended_ids = {rec.movie_id for rec in result}
    assert 2 not in recommended_ids
    assert 3 not in recommended_ids
    assert 100 in recommended_ids
    assert 101 in recommended_ids

def test_aggregates_scores_from_multiple_seeds(self, mocker, mock_repos):
    """Test that scores are aggregated across multiple seed movies."""
    mock_repos["ratings"].get_by_user.return_value = [
        {"movie_id": 1, "rating": 4.0},
        {"movie_id": 2, "rating": 5.0}
    ]
    mock_repos["movies"].get_by_id.side_effect = lambda mid: {"movieId": mid, "title": f"Movie {mid}"}
    
    def mock_get_similar(movie_id, limit):
        if movie_id == 1:
            return [
                RecommendationItem(movie_id=100, similarity_score=0.8),
                RecommendationItem(movie_id=101, similarity_score=0.7)
            ]
        elif movie_id == 2:
            return [
                RecommendationItem(movie_id=100, similarity_score=0.9),  # Overlaps
                RecommendationItem(movie_id=102, similarity_score=0.6)
            ]
        return []
    
    mocker.patch(
        "app.services.recommendations_service.get_similar_movies",
        side_effect=mock_get_similar
    )
    
    result = recommendations_service.generate_recommendations("user123", limit=10)
    
    movie_100 = next((r for r in result if r.movie_id == 100), None)
    assert movie_100 is not None
    # Score should be weighted average of 0.8 * (4.0/5) and 0.9 * (5.0/5)
    # = (0.64 + 0.9) / 2 = 0.77
    assert 0.7 <= movie_100.similarity_score <= 0.8

def test_sorts_recommendations_by_score(self, mocker, mock_repos):
    """Test that final recommendations are sorted by similarity score."""
    mock_repos["ratings"].get_by_user.return_value = [
        {"movie_id": 1, "rating": 4.5}
    ]
    mock_repos["movies"].get_by_id.side_effect = lambda mid: {"movieId": mid, "title": f"Movie {mid}"}
    
    mocker.patch(
        "app.services.recommendations_service.get_similar_movies",
        return_value=[
            RecommendationItem(movie_id=100, similarity_score=0.7),
            RecommendationItem(movie_id=101, similarity_score=0.9),
            RecommendationItem(movie_id=102, similarity_score=0.5),
            RecommendationItem(movie_id=103, similarity_score=0.95)
        ]
    )
    
    result = recommendations_service.generate_recommendations("user123", limit=10)
    
    scores = [rec.similarity_score for rec in result]
    assert scores == sorted(scores, reverse=True)
    assert result[0].movie_id == 103  # Highest score
    assert result[-1].movie_id == 102  # Lowest score

def test_uses_all_ratings_when_no_high_ratings(self, mocker, mock_repos):
    """Test that when user has no high ratings, top 5 ratings are used."""
    mock_repos["ratings"].get_by_user.return_value = [
        {"movie_id": 1, "rating": 3.5},
        {"movie_id": 2, "rating": 3.0},
        {"movie_id": 3, "rating": 2.5},
        {"movie_id": 4, "rating": 3.8},
        {"movie_id": 5, "rating": 2.0},
        {"movie_id": 6, "rating": 3.2}
    ]
    mock_repos["movies"].get_by_id.side_effect = lambda mid: {"movieId": mid, "title": f"Movie {mid}"}
    
    mock_get_similar = mocker.patch(
        "app.services.recommendations_service.get_similar_movies",
        return_value=[RecommendationItem(movie_id=100, similarity_score=0.8)]
    )
    
    result = recommendations_service.generate_recommendations("user123", limit=10)
    
    assert mock_get_similar.call_count <= 5
    
def test_returns_similar_movies_for_valid_movie(self, mocker, mock_repos, mock_recommender):
    """Test getting similar movies for a valid movie ID."""
    mock_repos["movies"].get_by_id.return_value = {
        "movieId": 1,
        "title": "The Matrix (1999)"
    }
    
    mock_recommender_instance = MagicMock()
    mock_recommender_instance.get_recommendations.return_value = [
        ("The Matrix Reloaded (2003)", 0.92),
        ("Inception (2010)", 0.88),
        ("Blade Runner (1982)", 0.85)
    ]
    mock_recommender.return_value = mock_recommender_instance
    
    def mock_search(title, limit):
        title_to_id = {
            "The Matrix Reloaded (2003)": 2,
            "Inception (2010)": 3,
            "Blade Runner (1982)": 4
        }
        movie_id = title_to_id.get(title)
        if movie_id:
            return [{"movieId": movie_id, "title": title}]
        return []
    
    mock_repos["movies"].search.side_effect = mock_search
    
    result = recommendations_service.get_similar_movies(1, limit=3)
    
    assert len(result) == 3
    assert result[0].movie_id == 2
    assert result[0].similarity_score == 0.92
    assert result[1].movie_id == 3
    assert result[2].movie_id == 4
    
    mock_repos["movies"].get_by_id.assert_called_once_with(1)
    mock_recommender_instance.get_recommendations.assert_called_once_with("The Matrix (1999)", n=3)

def test_returns_empty_for_invalid_movie(self, mock_repos, mock_recommender):
    """Test that invalid movie ID returns empty list."""
    mock_repos["movies"].get_by_id.return_value = None
    
    result = recommendations_service.get_similar_movies(99999, limit=5)
    
    assert result == []
    mock_recommender.assert_not_called()

def test_returns_empty_when_no_similar_movies(self, mocker, mock_repos, mock_recommender):
    """Test handling when recommender returns no results."""
    mock_repos["movies"].get_by_id.return_value = {
        "movieId": 1,
        "title": "Obscure Movie (2000)"
    }
    
    mock_recommender_instance = MagicMock()
    mock_recommender_instance.get_recommendations.return_value = None
    mock_recommender.return_value = mock_recommender_instance
    
    result = recommendations_service.get_similar_movies(1, limit=5)
    
    assert result == []

def test_handles_title_mismatch_gracefully(self, mocker, mock_repos, mock_recommender):
    """Test handling when search doesn't find exact title match."""
    mock_repos["movies"].get_by_id.return_value = {
        "movieId": 1,
        "title": "Test Movie (2000)"
    }
    
    mock_recommender_instance = MagicMock()
    mock_recommender_instance.get_recommendations.return_value = [
        ("Similar Movie 1 (2001)", 0.9),
        ("Similar Movie 2 (2002)", 0.8)
    ]
    mock_recommender.return_value = mock_recommender_instance
    
    mock_repos["movies"].search.return_value = [
        {"movieId": 100, "title": "Different Movie (2001)"}
    ]
    
    result = recommendations_service.get_similar_movies(1, limit=2)
    
    assert len(result) == 0

def test_calls_get_recommendations_with_force_refresh(self, mocker):
    """Test that refresh calls get_recommendations with force_refresh=True."""
    mock_get_recommendations = mocker.patch(
        "app.services.recommendations_service.get_recommendations",
        return_value=MagicMock(user_id="user123", recommendations=[])
    )
    
    result = recommendations_service.refresh_recommendations_for_user("user123", limit=15)
    
    mock_get_recommendations.assert_called_once_with("user123", limit=15, force_refresh=True)

def test_calls_repository_clear_method(self, mock_repos):
    """Test that cache clearing delegates to repository."""
    recommendations_service.clear_recommendations_cache("user123")
    
    mock_repos["recommendations"].clear_for_user.assert_called_once_with("user123")

def test_returns_movies_with_default_score(self, mock_repos):
    """Test that fallback returns movies with neutral similarity score."""
    mock_repos["movies"].get_all.return_value = [
        {"movieId": 1, "title": "Movie 1"},
        {"movieId": 2, "title": "Movie 2"},
        {"movieId": 3, "title": "Movie 3"}
    ]
    
    result = recommendations_service._get_fallback_recommendations(limit=3)
    
    assert len(result) == 3
    assert all(rec.similarity_score == 0.5 for rec in result)
    assert result[0].movie_id == 1
    assert result[1].movie_id == 2
    assert result[2].movie_id == 3
    mock_repos["movies"].get_all.assert_called_once_with(limit=3)

def test_respects_limit_parameter(self, mock_repos):
    """Test that fallback respects limit parameter."""
    mock_repos["movies"].get_all.return_value = [
        {"movieId": i, "title": f"Movie {i}"} for i in range(20)
    ]
    
    result = recommendations_service._get_fallback_recommendations(limit=5)
    
    assert len(result) == 5
    mock_repos["movies"].get_all.assert_called_once_with(limit=5)

def test_recommender_is_singleton(self, mocker):
    """Test that recommender is only initialized once."""
    recommendations_service._recommender = None
    
    mock_recommender_class = mocker.patch(
        "app.services.recommendations_service.MovieRecommender"
    )
    mock_instance = MagicMock()
    mock_recommender_class.return_value = mock_instance
    
    rec1 = recommendations_service._get_recommender()
    rec2 = recommendations_service._get_recommender()
    rec3 = recommendations_service._get_recommender()
    
    assert mock_recommender_class.call_count == 1
    assert rec1 is rec2
    assert rec2 is rec3