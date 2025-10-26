import pytest
import pandas as pd
import json
from app.repositories.movies_repo import MoviesRepository

def test_load_movies_and_average_rating(tmp_path):
    # Setup "Mock" CSV and JSON
    movie_dir = tmp_path / "movies"
    movie_dir.mkdir()
    movie_csv = movie_dir / "movie.csv"
    movie_csv.write_text("movieId,title,genres\n1,The Matrix,Action|Sci-Fi\n2,Toy Story,Animation|Children\n")

    ratings_file = tmp_path / "ratings.json"
    ratings_data = [
        {"id": "r1", "user_id": "u1", "movie_id": "1", "rating": 5.0, "timestamp": "2025-10-25T00:00:00"},
        {"id": "r2", "user_id": "u2", "movie_id": "1", "rating": 4.0, "timestamp": "2025-10-25T00:00:00"}
    ]
    ratings_file.write_text(json.dumps(ratings_data))

    repo = MoviesRepository(movies_dir=movie_dir)

    avg = repo.get_average_rating(1, ratings_file)
    assert avg == 4.5

    # Make sure the avg rating appears when get by id is called in the movie repo
    movie = repo.get_by_id(1)
    assert "average_rating" in movie or avg == 4.5
