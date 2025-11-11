"""Unit tests for recommendations repository."""
import pytest
from datetime import datetime, timezone, timedelta
from app.repositories.recommendations_repo import RecommendationsRepository

@pytest.fixture
def repo(mocker):
    mock_path = mocker.MagicMock()
    mock_path.exists.return_value = True
    mock_path.parent.mkdir = mocker.Mock()
    mock_path.write_text = mocker.Mock()
    mocker.patch("app.repositories.recommendations_repo.Path", return_value=mock_path)

    repo = RecommendationsRepository()

    mocker.patch.object(repo, "_read", return_value={})
    mocker.patch.object(repo, "_write")
    return repo


def test_ensure_file_created_if_missing(mocker):
    mock_path = mocker.MagicMock()
    mock_path.exists.return_value = False
    mock_path.parent.mkdir = mocker.Mock()
    mock_path.write_text = mocker.Mock()
    mocker.patch("app.repositories.recommendations_repo.Path", return_value=mock_path)

    repo = RecommendationsRepository()
    mock_path.write_text.assert_called_once_with("{}", encoding="utf-8")
    mock_path.parent.mkdir.assert_called_once()

def test_save_for_user(repo):
    recs = [{"movie_id": 42, "similarity_score": 0.99}]
    repo.save_for_user("alice", recs)

    written = repo._write.call_args[0][0]
    assert "alice" in written
    assert "timestamp" in written["alice"]
    assert written["alice"]["recommendations"][0]["movie_id"] == 42

def test_get_for_user(mocker):
    repo = RecommendationsRepository()
    mocker.patch.object(
        repo,
        "_read",
        return_value={
            "bob": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "recommendations": [{"movie_id": 7, "similarity_score": 0.8}],
            }
        },
    )

    result = repo.get_for_user("bob")
    assert result is not None
    assert result["recommendations"][0]["movie_id"] == 7

def test_get_for_nonexistent_user(mocker):
    repo = RecommendationsRepository()
    mocker.patch.object(repo, "_read", return_value={})
    assert repo.get_for_user("ghost") is None

def test_clear_for_user(mocker):
    repo = RecommendationsRepository()
    mocker.patch.object(repo, "_read", return_value={"u1": {}, "u2": {}})
    mock_write = mocker.patch.object(repo, "_write")

    repo.clear_for_user("u1")
    result = mock_write.call_args[0][0] 
    assert "u1" not in result and "u2" in result

def test_is_fresh_true(mocker):
    repo = RecommendationsRepository()
    now = datetime.now(timezone.utc)
    mocker.patch.object(
        repo, "get_for_user", return_value={"timestamp": now.isoformat()}
    )
    assert repo.is_fresh("u", max_age_hours=24)

def test_is_fresh_false_for_old(mocker):
    repo = RecommendationsRepository()
    old = datetime.now(timezone.utc) - timedelta(hours=25)
    mocker.patch.object(
        repo, "get_for_user", return_value={"timestamp": old.isoformat()}
    )
    assert not repo.is_fresh("u", max_age_hours=24)

def test_is_fresh_false_for_missing_user(mocker):
    repo = RecommendationsRepository()
    mocker.patch.object(repo, "get_for_user", return_value=None)
    assert not repo.is_fresh("u")

def test_is_fresh_false_for_invalid_timestamp(mocker):
    repo = RecommendationsRepository()
    mocker.patch.object(repo, "get_for_user", return_value={"timestamp": "nonsense"})
    assert not repo.is_fresh("u")

def test_overwrites_existing_user(repo):
    repo._read.return_value = {"x": {"recommendations": []}}
    recs = [
        {"movie_id": 1, "similarity_score": 0.5},
        {"movie_id": 2, "similarity_score": 0.4},
    ]
    repo.save_for_user("x", recs)

    written = repo._write.call_args[0][0]
    assert len(written["x"]["recommendations"]) == 2
    assert written["x"]["recommendations"][0]["movie_id"] == 1

def test_handles_corrupted_json(mocker):
    repo = RecommendationsRepository()
    mocker.patch.object(repo, "_read", side_effect=Exception("bad json"))
    try:
        repo.get_for_user("x")
    except Exception:
        pytest.fail("get_for_user() raised despite _read() exception")

def test_timestamp_format(repo):
    recs = [{"movie_id": 99, "similarity_score": 0.7}]
    repo.save_for_user("tim", recs)

    saved = repo._write.call_args[0][0]
    ts = saved["tim"]["timestamp"]
    parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    assert isinstance(parsed, datetime)
