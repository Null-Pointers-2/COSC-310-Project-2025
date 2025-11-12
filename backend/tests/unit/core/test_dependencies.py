"""Unit tests for core dependencies."""

from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

from fastapi import HTTPException
import jwt
import pytest

from app.core.config import settings
from app.core.dependencies import decode_token, get_current_active_user, get_current_admin_user, get_current_user


@pytest.fixture
def mock_users_repo():
    repo = Mock()
    repo.get_by_username.return_value = {
        "id": "user123",
        "username": "testuser",
        "email": "test@example.com",
        "role": "user",
    }
    return repo


@pytest.fixture
def mock_penalties_repo():
    repo = Mock()
    repo.get_active_by_user.return_value = []
    return repo


@pytest.fixture
def mock_resources(mock_users_repo, mock_penalties_repo):
    resources = Mock()
    resources.users_repo = mock_users_repo
    resources.penalties_repo = mock_penalties_repo
    return resources


@pytest.fixture
def valid_token():
    payload = {
        "sub": "testuser",
        "exp": datetime.now(UTC) + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def test_decode_token_success(mock_users_repo, valid_token):
    result = decode_token(valid_token, mock_users_repo)

    assert result["user_id"] == "user123"
    assert result["username"] == "testuser"
    assert result["role"] == "user"


def test_decode_token_missing_sub(mock_users_repo):
    payload = {"exp": datetime.now(UTC) + timedelta(hours=1)}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    with pytest.raises(HTTPException) as exc_info:
        decode_token(token, mock_users_repo)

    assert exc_info.value.status_code == 401


def test_decode_token_user_not_found(mock_users_repo, valid_token):
    mock_users_repo.get_by_username.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        decode_token(valid_token, mock_users_repo)

    assert exc_info.value.status_code == 401
    assert "User not found" in str(exc_info.value.detail)


def test_decode_token_invalid_token(mock_users_repo):
    with pytest.raises(HTTPException) as exc_info:
        decode_token("invalid_token", mock_users_repo)

    assert exc_info.value.status_code == 401


def test_decode_token_expired(mock_users_repo):
    payload = {
        "sub": "testuser",
        "exp": datetime.now(UTC) - timedelta(hours=1),  # Expired
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    with pytest.raises(HTTPException) as exc_info:
        decode_token(token, mock_users_repo)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_success(mock_resources, valid_token):
    user = await get_current_user(token=valid_token, resources=mock_resources)

    assert user["id"] == "user123"
    assert user["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_resources):
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token="invalid_token", resources=mock_resources)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_user_deleted(mock_resources, valid_token):
    mock_resources.users_repo.get_by_username.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=valid_token, resources=mock_resources)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_active_user_success(mock_resources):
    current_user = {"id": "user123", "username": "testuser", "role": "user"}
    mock_resources.penalties_repo.get_active_by_user.return_value = []

    result = await get_current_active_user(current_user=current_user, resources=mock_resources)

    assert result == current_user


@pytest.mark.asyncio
async def test_get_current_active_user_with_penalties(mock_resources):
    current_user = {"id": "user123", "username": "testuser", "role": "user"}
    mock_resources.penalties_repo.get_active_by_user.return_value = [
        {"id": "p1", "reason": "Spam", "status": "active"},
    ]

    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(current_user=current_user, resources=mock_resources)

    assert exc_info.value.status_code == 403
    assert "active penalties" in str(exc_info.value.detail).lower()


@pytest.mark.asyncio
async def test_get_current_active_user_with_multiple_penalties(mock_resources):
    current_user = {"id": "user123", "username": "testuser", "role": "user"}
    mock_resources.penalties_repo.get_active_by_user.return_value = [
        {"id": "p1", "reason": "Spam", "status": "active"},
        {"id": "p2", "reason": "Harassment", "status": "active"},
    ]

    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(current_user=current_user, resources=mock_resources)

    assert exc_info.value.status_code == 403
    detail = str(exc_info.value.detail).lower()
    assert "spam" in detail
    assert "harassment" in detail


@pytest.mark.asyncio
async def test_get_current_admin_user_success():
    admin_user = {"id": "admin123", "username": "admin", "role": "admin"}

    result = await get_current_admin_user(current_user=admin_user)

    assert result == admin_user


@pytest.mark.asyncio
async def test_get_current_admin_user_not_admin():
    regular_user = {"id": "user123", "username": "testuser", "role": "user"}

    with pytest.raises(HTTPException) as exc_info:
        await get_current_admin_user(current_user=regular_user)

    assert exc_info.value.status_code == 403
    assert "Admin privileges required" in str(exc_info.value.detail)


def test_decode_token_verifies_username(mock_users_repo, valid_token):
    decode_token(valid_token, mock_users_repo)

    mock_users_repo.get_by_username.assert_called_once_with("testuser")


@pytest.mark.asyncio
async def test_get_current_user_checks_penalties(mock_resources, valid_token):
    current_user = {"id": "user123", "username": "testuser", "role": "user"}

    await get_current_active_user(current_user=current_user, resources=mock_resources)

    mock_resources.penalties_repo.get_active_by_user.assert_called_once_with("user123")
