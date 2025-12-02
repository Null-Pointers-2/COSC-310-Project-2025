"""Unit tests for global insights service."""

from unittest.mock import Mock

from app.services.global_insights_service import (
    _calculate_popularity_score,
    get_global_genre_leaderboard,
)


# Tests for _calculate_popularity_score
def test_calculate_popularity_score_general():
    """Test general case popularity score calculation."""
    score = _calculate_popularity_score(total_ratings=50, avg_rating=4.0, total_platform_ratings=100)
    assert 66 <= score <= 67


def test_calculate_popularity_score_perfect():
    """Test perfect score edge case."""
    score = _calculate_popularity_score(total_ratings=100, avg_rating=5.0, total_platform_ratings=100)
    assert score == 100.0


def test_calculate_popularity_score_zero_platform_ratings():
    """Test edge case with zero platform ratings."""
    score = _calculate_popularity_score(total_ratings=0, avg_rating=0.0, total_platform_ratings=0)
    assert score == 0.0


def test_calculate_popularity_score_data_retrieval():
    """Test that popularity score uses correct formula parameters."""
    score1 = _calculate_popularity_score(total_ratings=200, avg_rating=1.0, total_platform_ratings=100)
    assert 46 <= score1 <= 47
    score2 = _calculate_popularity_score(total_ratings=10, avg_rating=5.0, total_platform_ratings=100)
    assert 63 <= score2 <= 65


# Tests for get_global_genre_leaderboard
def test_get_global_genre_leaderboard_general():
    """Test general case with multiple users and genres."""
    resources = Mock()
    resources.users_repo.get_all.return_value = [{"id": "user1"}, {"id": "user2"}]

    def get_ratings(user_id):
        if user_id == "user1":
            return [{"movie_id": 1, "rating": 5.0}, {"movie_id": 2, "rating": 4.0}]
        if user_id == "user2":
            return [{"movie_id": 1, "rating": 4.5}, {"movie_id": 3, "rating": 3.0}]
        return []

    resources.ratings_repo.get_by_user.side_effect = get_ratings

    def get_movie(movie_id):
        movies = {1: {"genres": ["Action", "Sci-Fi"]}, 2: {"genres": ["Action"]}, 3: {"genres": ["Drama"]}}
        return movies.get(movie_id)

    resources.movies_repo.get_by_id.side_effect = get_movie

    result = get_global_genre_leaderboard(resources)

    assert result.total_users == 2
    assert result.total_ratings == 4
    assert len(result.genres) == 3
    action_genre = next(g for g in result.genres if g.genre == "Action")
    assert action_genre.total_ratings == 3
    assert action_genre.user_count == 2


def test_get_global_genre_leaderboard_no_users():
    """Test edge case with no users."""
    resources = Mock()
    resources.users_repo.get_all.return_value = []

    result = get_global_genre_leaderboard(resources)

    assert result.total_users == 0
    assert result.total_ratings == 0
    assert result.genres == []


def test_get_global_genre_leaderboard_missing_movie_data():
    """Test edge case with missing or invalid movie data."""
    resources = Mock()
    resources.users_repo.get_all.return_value = [{"id": "user1"}]
    resources.ratings_repo.get_by_user.return_value = [
        {"movie_id": 1, "rating": 5.0},
        {"movie_id": 2, "rating": 4.0},
        {"movie_id": 3, "rating": 3.0},
    ]

    def get_movie(movie_id):
        if movie_id == 1:
            return None
        if movie_id == 2:
            return {"genres": []}
        if movie_id == 3:
            return {"genres": ["Action", "", None]}
        return None

    resources.movies_repo.get_by_id.side_effect = get_movie

    result = get_global_genre_leaderboard(resources)

    assert result.total_users == 1
    assert result.total_ratings == 1
    assert len(result.genres) == 1
    assert result.genres[0].genre == "Action"


def test_get_global_genre_leaderboard_data_retrieval():
    """Test that leaderboard correctly retrieves and processes all data."""
    resources = Mock()
    resources.users_repo.get_all.return_value = [{"id": "user1"}, {"id": "user2"}, {"id": "user3"}]

    def get_ratings(user_id):
        if user_id == "user1":
            return [{"movie_id": 1, "rating": 5.0}, {"movie_id": 2, "rating": 4.0}]
        if user_id == "user2":
            return [{"movie_id": 1, "rating": 4.5}]
        if user_id == "user3":
            return [{"movie_id": 3, "rating": 3.0}]
        return []

    resources.ratings_repo.get_by_user.side_effect = get_ratings

    def get_movie(movie_id):
        movies = {1: {"genres": ["Action"]}, 2: {"genres": ["Comedy"]}, 3: {"genres": ["Drama"]}}
        return movies.get(movie_id)

    resources.movies_repo.get_by_id.side_effect = get_movie

    result = get_global_genre_leaderboard(resources)

    assert resources.users_repo.get_all.call_count == 1
    assert resources.ratings_repo.get_by_user.call_count == 3
    assert result.total_users == 3
    assert result.total_ratings == 4

    action_genre = next(g for g in result.genres if g.genre == "Action")
    assert action_genre.total_ratings == 2
    assert action_genre.user_count == 2
    assert action_genre.average_rating == 4.75
