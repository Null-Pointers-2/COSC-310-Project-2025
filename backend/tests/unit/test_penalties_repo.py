"""Unit tests for penalties repository."""

import json

import pytest

from app.repositories.penalties_repo import PenaltiesRepository


@pytest.fixture
def repo(tmp_path):
    test_file = tmp_path / "penalties.json"
    return PenaltiesRepository(penalties_file=test_file)


def test_initialization_creates_file(tmp_path):
    test_file = tmp_path / "penalties.json"
    repo = PenaltiesRepository(penalties_file=test_file)

    assert test_file.exists()
    assert json.loads(test_file.read_text()) == []


def test_handles_corrupted_json(tmp_path):
    test_file = tmp_path / "penalties.json"
    test_file.write_text("invalid json")

    repo = PenaltiesRepository(penalties_file=test_file)
    assert repo.get_all() == []


def test_create_penalty(repo):
    penalty_data = {
        "user_id": "user123",
        "reason": "Spam",
        "description": "Posted 100 ratings in 1 minute",
        "issued_by": "admin1",
    }

    created = repo.create(penalty_data)

    assert "id" in created
    assert created["user_id"] == "user123"
    assert created["reason"] == "Spam"
    assert created["description"] == "Posted 100 ratings in 1 minute"
    assert created["status"] == "active"
    assert created["issued_by"] == "admin1"
    assert created["issued_at"] is not None
    assert created["resolved_at"] is None


def test_get_by_id(repo):
    created = repo.create(
        {
            "user_id": "user123",
            "reason": "Spam",
            "description": "Test",
            "issued_by": "admin1",
        }
    )

    fetched = repo.get_by_id(created["id"])
    assert fetched == created


def test_get_by_id_returns_none(repo):
    assert repo.get_by_id("non-existent-id") is None


def test_get_by_user(repo):
    repo.create(
        {
            "user_id": "user1",
            "reason": "Spam",
            "description": None,
            "issued_by": "admin1",
        }
    )
    repo.create(
        {
            "user_id": "user1",
            "reason": "Inappropriate content",
            "description": None,
            "issued_by": "admin1",
        }
    )
    repo.create(
        {
            "user_id": "user2",
            "reason": "Spam",
            "description": None,
            "issued_by": "admin1",
        }
    )

    user1_penalties = repo.get_by_user("user1")
    assert len(user1_penalties) == 2
    assert all(p["user_id"] == "user1" for p in user1_penalties)


def test_get_active_by_user(repo):
    p1 = repo.create(
        {
            "user_id": "user1",
            "reason": "Spam",
            "description": None,
            "issued_by": "admin1",
        }
    )
    repo.create(
        {
            "user_id": "user1",
            "reason": "Harassment",
            "description": None,
            "issued_by": "admin1",
        }
    )

    repo.resolve(p1["id"])

    active = repo.get_active_by_user("user1")
    assert len(active) == 1
    assert active[0]["status"] == "active"
    assert active[0]["reason"] == "Harassment"


def test_get_all(repo):
    repo.create(
        {
            "user_id": "user1",
            "reason": "Spam",
            "description": None,
            "issued_by": "admin1",
        }
    )
    repo.create(
        {
            "user_id": "user2",
            "reason": "Harassment",
            "description": None,
            "issued_by": "admin1",
        }
    )

    all_penalties = repo.get_all()
    assert len(all_penalties) == 2


def test_update_penalty(repo):
    created = repo.create(
        {
            "user_id": "user1",
            "reason": "Spam",
            "description": "Original description",
            "issued_by": "admin1",
        }
    )

    updated = repo.update(created["id"], {"description": "Updated description"})

    assert updated["description"] == "Updated description"
    assert updated["reason"] == "Spam"  # Other fields should be unchanged


def test_update_nonexistent_returns_none(repo):
    result = repo.update("non-existent-id", {"description": "Test"})
    assert result is None


def test_resolve_penalty(repo):
    created = repo.create(
        {
            "user_id": "user1",
            "reason": "Spam",
            "description": None,
            "issued_by": "admin1",
        }
    )

    success = repo.resolve(created["id"])
    assert success is True

    resolved = repo.get_by_id(created["id"])
    assert resolved["status"] == "resolved"
    assert resolved["resolved_at"] is not None


def test_resolve_nonexistent_returns_false(repo):
    success = repo.resolve("non-existent-id")
    assert success is False


def test_delete_penalty(repo):
    created = repo.create(
        {
            "user_id": "user1",
            "reason": "Spam",
            "description": None,
            "issued_by": "admin1",
        }
    )

    success = repo.delete(created["id"])
    assert success is True
    assert repo.get_by_id(created["id"]) is None


def test_delete_nonexistent_returns_false(repo):
    success = repo.delete("non-existent-id")
    assert success is False


def test_penalty_persistence(tmp_path):
    test_file = tmp_path / "penalties.json"

    repo1 = PenaltiesRepository(penalties_file=test_file)
    created = repo1.create(
        {
            "user_id": "user1",
            "reason": "Spam",
            "description": None,
            "issued_by": "admin1",
        }
    )

    repo2 = PenaltiesRepository(penalties_file=test_file)
    fetched = repo2.get_by_id(created["id"])

    assert fetched == created
