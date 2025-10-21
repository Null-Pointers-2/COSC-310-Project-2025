import pytest
import json
import csv
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def test_data_dir(tmp_path):
    """Create a temporary directory for test data files."""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    return data_dir

@pytest.fixture
def sample_users(test_data_dir):
    """Create sample users CSV file."""
    users_file = test_data_dir / "users.csv"
    users = [
        {"id": "1", "username": "admin", "password": "admin123", "role": "admin", "email": "admin@test.com"},
        {"id": "2", "username": "user1", "password": "user123", "role": "user", "email": "user1@test.com"},
        {"id": "3", "username": "user2", "password": "user123", "role": "user", "email": "user2@test.com"}
    ]
    
    with open(users_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=users[0].keys())
        writer.writeheader()
        writer.writerows(users)
    
    return users_file

@pytest.fixture
def sample_movies(test_data_dir):
    """Create sample movies CSV file."""
    movies_file = test_data_dir / "movies.csv"
    movies = [
        {"id": "1", "title": "The Matrix", "year": "1999", "genre": "Sci-Fi"},
        {"id": "2", "title": "Inception", "year": "2010", "genre": "Sci-Fi"},
        {"id": "3", "title": "The Godfather", "year": "1972", "genre": "Crime"}
    ]
    
    with open(movies_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=movies[0].keys())
        writer.writeheader()
        writer.writerows(movies)
    
    return movies_file

@pytest.fixture
def sample_items_json(test_data_dir):
    """Create sample items JSON file."""
    items_file = test_data_dir / "items.json"
    items = [
        {"id": "1", "user_id": "2", "movie_id": "1", "status": "rented", "due_date": "2025-11-01"},
        {"id": "2", "user_id": "3", "movie_id": "2", "status": "saved", "due_date": None}
    ]
    
    with open(items_file, 'w') as f:
        json.dump(items, f, indent=2)
    
    return items_file

@pytest.fixture
def auth_headers_admin(client):
    """Get authentication headers for admin user."""
    response = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_headers_user(client):
    """Get authentication headers for regular user."""
    response = client.post("/auth/login", json={
        "username": "user1",
        "password": "user123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def reset_data_files():
    """Reset data files before each test (if needed)."""
    yield
    # Cleanup after test if needed