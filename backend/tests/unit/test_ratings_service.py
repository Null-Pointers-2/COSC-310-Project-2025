import pytest
from app.services import ratings_service
from app.repositories.ratings_repo import RatingsRepository

def test_create_and_update_rating(monkeypatch, tmp_path):
    # Temporary repo for testing
    test_file = tmp_path / "ratings.json"
    repo = RatingsRepository(ratings_file=test_file)

    # Mock global repo used in service
    ratings_service.ratings_repo = repo
    ratings_service.recommendations_repo.clear_cache = lambda user_id: None  # disable cache calls

    r1 = ratings_service.create_rating("u1", type("RatingCreate", (), {"movie_id": "m1", "rating": 4.0}))
    assert r1.rating == 4.0

    # Test rating a movie twice
    r2 = ratings_service.create_rating("u1", type("RatingCreate", (), {"movie_id": "m1", "rating": 5.0}))
    assert r2.rating == 5.0

    all_ratings = repo.get_all()
    assert len(all_ratings) == 1

def test_delete_rating(tmp_path):
    test_file = tmp_path / "ratings.json"
    repo = RatingsRepository(ratings_file=test_file)
    ratings_service.ratings_repo = repo
    ratings_service.recommendations_repo.clear_cache = lambda user_id: None

    created = repo.create({"user_id": "u2", "movie_id": "m2", "rating": 3.0})
    deleted = ratings_service.delete_rating(created["id"], "u2")
    assert deleted is True
