import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import export


def mock_get_current_user():
    """Mock for dependency override. Returns a static user."""
    return {"id": "user123", "username": "testuser", "role": "user"}


def mock_get_user_profile(user_id, resources):
    """Mock for users_service.get_user_profile."""
    return {"id": user_id, "name": "Test User", "email": "test@example.com"}


@pytest.fixture
def test_app(mocker):
    """Build a FastAPI app with mocked dependencies."""
    app = FastAPI()
    app.include_router(export.router, prefix="/export")

    app.dependency_overrides[export.get_current_user] = mock_get_current_user

    mock_res = mocker.MagicMock()
    app.dependency_overrides[export.get_resources] = lambda: mock_res

    mocker.patch.object(export.users_service, "get_user_profile", new=mock_get_user_profile)

    mocker.patch.object(
        export.ratings_service,
        "get_user_ratings",
        return_value=[{"movie_id": 1, "rating": 5}, {"movie_id": 2, "rating": 3}],
    )

    mocker.patch.object(export.watchlist_service, "get_user_watchlist", return_value=[10, 20, 30])

    mock_reco_list = mocker.MagicMock()
    mock_reco_list.model_dump.return_value = {
        "user_id": "user123",
        "recommendations": [{"movie_id": 99, "score": 0.87}],
    }
    mocker.patch.object(export.recommendations_service, "get_recommendations", return_value=mock_reco_list)

    return app


@pytest.fixture
def empty_test_app(mocker):
    """Build a FastAPI app with mocked dependencies that return empty data."""
    app = FastAPI()
    app.include_router(export.router, prefix="/export")

    app.dependency_overrides[export.get_current_user] = mock_get_current_user

    mock_res = mocker.MagicMock()
    app.dependency_overrides[export.get_resources] = lambda: mock_res

    mocker.patch.object(export.users_service, "get_user_profile", return_value={})

    mocker.patch.object(export.ratings_service, "get_user_ratings", return_value=[])

    mocker.patch.object(export.watchlist_service, "get_user_watchlist", return_value=[])

    mock_reco_list = mocker.MagicMock()
    mock_reco_list.model_dump.return_value = {"user_id": "user123", "recommendations": []}
    mocker.patch.object(export.recommendations_service, "get_recommendations", return_value=mock_reco_list)

    return app


# --- Tests -----------------------------------------------------------------


def test_export_profile(test_app):
    client = TestClient(test_app)

    resp = client.get("/export/profile")
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"

    assert "attachment" in resp.headers["content-disposition"]


def test_export_ratings(test_app):
    client = TestClient(test_app)

    resp = client.get("/export/ratings")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
    assert resp.json()[0]["movie_id"] == 1


def test_export_watchlist(test_app):
    client = TestClient(test_app)

    resp = client.get("/export/watchlist")
    assert resp.status_code == 200
    assert resp.json() == [10, 20, 30]


def test_export_recommendations(test_app):
    client = TestClient(test_app)

    resp = client.get("/export/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == "user123"
    assert len(data["recommendations"]) == 1


def test_export_all(test_app):
    client = TestClient(test_app)

    resp = client.get("/export/export_all")
    assert resp.status_code == 200

    data = resp.json()
    assert "profile" in data
    assert "ratings" in data
    assert "watchlist" in data
    assert "recommendations" in data

    assert data["profile"]["name"] == "Test User"
    assert len(data["ratings"]) == 2
    assert data["watchlist"] == [10, 20, 30]

    # --- Empty Field Tests -----------------------------------------------------------------


def test_export_profile_empty(empty_test_app):
    client = TestClient(empty_test_app)
    resp = client.get("/export/profile")
    assert resp.status_code == 200
    assert resp.json() == {}


def test_export_ratings_empty(empty_test_app):
    client = TestClient(empty_test_app)
    resp = client.get("/export/ratings")
    assert resp.status_code == 200
    assert resp.json() == []


def test_export_watchlist_empty(empty_test_app):
    client = TestClient(empty_test_app)
    resp = client.get("/export/watchlist")
    assert resp.status_code == 200
    assert resp.json() == []


def test_export_recommendations_empty(empty_test_app):
    client = TestClient(empty_test_app)
    resp = client.get("/export/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == "user123"
    assert data["recommendations"] == []
    assert len(data["recommendations"]) == 0


def test_export_all_empty(empty_test_app):
    client = TestClient(empty_test_app)
    resp = client.get("/export/export_all")
    assert resp.status_code == 200

    data = resp.json()
    assert "profile" in data
    assert "ratings" in data
    assert "watchlist" in data
    assert "recommendations" in data

    assert data["profile"] == {}
    assert data["ratings"] == []
    assert data["watchlist"] == []
    assert data["recommendations"]["user_id"] == "user123"
    assert data["recommendations"]["recommendations"] == []
