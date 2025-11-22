"""Unit tests for users repository."""

import csv

import pytest

from app.repositories.users_repo import UsersRepository


@pytest.fixture
def repo(tmp_path):
    return UsersRepository(users_file=tmp_path / "users.csv")


@pytest.fixture
def user_data():
    return {
        "username": "bob",
        "email": "bob@example.com",
        "hashed_password": "supersecurepassword",
        "role": "user",
        "created_at": "2025-10-21",
    }


def test_crud(repo, user_data, mocker):
    mocker.patch("app.repositories.users_repo.uuid4", return_value="uid-123")

    user = repo.create(user_data)
    assert user["id"] == "uid-123"
    assert user["username"] == "bob"

    assert repo.get_by_id("uid-123") == user

    updated = repo.update("uid-123", {"email": "bob@example.com"})
    assert updated["email"] == "bob@example.com"
    assert updated["id"] == "uid-123"

    assert repo.delete("uid-123") is True
    assert repo.get_by_id("uid-123") is None


def test_retrieval(repo, user_data):
    repo.create(user_data)

    assert repo.get_by_username("bob") is not None
    assert repo.get_by_email("bob@example.com") is not None
    assert len(repo.get_all()) == 1

    assert repo.get_by_username("ghost") is None
    assert repo.get_by_email("ghost@example.com") is None
    assert repo.delete("ghost-id") is False


def test_persistence(tmp_path, user_data):
    file_path = tmp_path / "users.csv"

    repo1 = UsersRepository(users_file=file_path)
    repo1.create(user_data)

    repo2 = UsersRepository(users_file=file_path)
    users = repo2.get_all()

    assert len(users) == 1
    assert users[0]["username"] == "bob"
