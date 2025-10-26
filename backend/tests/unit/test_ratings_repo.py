import pytest
from datetime import datetime
from app.repositories.ratings_repo import RatingsRepository

# Mock ratings for movie testing
def test_create_and_get_by_id(tmp_path):
    test_file = tmp_path / "ratings.json"
    repo = RatingsRepository(ratings_file=test_file)

    rating_data = {
        "user_id": "u1",
        "movie_id": "m1",
        "rating": 4.5
    }

    created = repo.create(rating_data)
    assert created["user_id"] == "u1"
    assert created["rating"] == 4.5

    fetched = repo.get_by_id(created["id"])
    assert fetched is not None
    assert fetched["movie_id"] == "m1"

def test_update_and_delete(tmp_path):
    test_file = tmp_path / "ratings.json"
    repo = RatingsRepository(ratings_file=test_file)

    created = repo.create({"user_id": "u2", "movie_id": "m2", "rating": 3.0})
    updated = repo.update(created["id"], {"rating": 4.0})
    assert updated["rating"] == 4.0

    deleted = repo.delete(created["id"])
    assert deleted is True
    assert repo.get_by_id(created["id"]) is None
