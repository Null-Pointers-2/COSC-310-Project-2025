"""Unit tests for ratings repository."""

import json

import pytest

from app.repositories.ratings_repo import RatingsRepository


@pytest.fixture
def repo(tmp_path):
    test_file = tmp_path / "ratings.json"
    return RatingsRepository(ratings_file=test_file)


def test_initialization_creates_file(tmp_path):
    test_file = tmp_path / "ratings.json"
    repo = RatingsRepository(ratings_file=test_file)

    assert test_file.exists()
    assert json.loads(test_file.read_text()) == []


def test_handles_corrupted_json(tmp_path):
    test_file = tmp_path / "ratings.json"
    test_file.write_text("invalid json")

    repo = RatingsRepository(ratings_file=test_file)
    assert repo.get_all() == []


def test_create_and_get_by_id(repo):
    created = repo.create({"user_id": "u1", "movie_id": 1, "rating": 4.5})

    assert created["id"] == 1
    assert created["user_id"] == "u1"
    assert created["movie_id"] == 1
    assert created["rating"] == 4.5
    assert "timestamp" in created

    fetched = repo.get_by_id(1)
    assert fetched == created


def test_get_by_id_returns_none(repo):
    assert repo.get_by_id(999) is None


def test_get_by_user(repo):
    repo.create({"user_id": "u1", "movie_id": 1, "rating": 4.0})
    repo.create({"user_id": "u1", "movie_id": 2, "rating": 5.0})
    repo.create({"user_id": "u2", "movie_id": 1, "rating": 3.0})

    user1_ratings = repo.get_by_user("u1")
    assert len(user1_ratings) == 2
    assert all(r["user_id"] == "u1" for r in user1_ratings)


def test_get_by_movie(repo):
    repo.create({"user_id": "u1", "movie_id": 100, "rating": 4.0})
    repo.create({"user_id": "u2", "movie_id": 100, "rating": 5.0})
    repo.create({"user_id": "u3", "movie_id": 200, "rating": 3.0})

    movie_ratings = repo.get_by_movie(100)
    assert len(movie_ratings) == 2
    assert all(r["movie_id"] == 100 for r in movie_ratings)


def test_get_by_user_and_movie(repo):
    repo.create({"user_id": "u1", "movie_id": 100, "rating": 4.0})
    repo.create({"user_id": "u2", "movie_id": 100, "rating": 5.0})

    rating = repo.get_by_user_and_movie("u1", 100)
    assert rating["user_id"] == "u1"
    assert rating["movie_id"] == 100

    assert repo.get_by_user_and_movie("u3", 100) is None


def test_update(repo):
    created = repo.create({"user_id": "u1", "movie_id": 1, "rating": 4.0})

    updated = repo.update(created["id"], {"rating": 5.0})
    assert updated["rating"] == 5.0
    assert updated["timestamp"] != created["timestamp"]
    assert updated["user_id"] == "u1"


def test_update_returns_none(repo):
    assert repo.update(999, {"rating": 5.0}) is None


def test_delete(repo):
    created = repo.create({"user_id": "u1", "movie_id": 1, "rating": 4.0})

    assert repo.delete(created["id"]) is True
    assert repo.get_by_id(created["id"]) is None


def test_delete_returns_false(repo):
    assert repo.delete(999) is False


def test_get_all(repo):
    repo.create({"user_id": "u1", "movie_id": 1, "rating": 4.0})
    repo.create({"user_id": "u2", "movie_id": 2, "rating": 5.0})

    all_ratings = repo.get_all()
    assert len(all_ratings) == 2


def test_id_increments(repo):
    r1 = repo.create({"user_id": "u1", "movie_id": 1, "rating": 4.0})
    r2 = repo.create({"user_id": "u2", "movie_id": 2, "rating": 5.0})

    assert r1["id"] == 1
    assert r2["id"] == 2
