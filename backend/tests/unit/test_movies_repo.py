import pytest
import json
from app.repositories.movies_repo import MoviesRepository

@pytest.fixture
def setup_movie_data(tmp_path):
    movie_dir = tmp_path / "movies"
    movie_dir.mkdir()
    movie_csv = movie_dir / "movies.csv"
    movie_csv.write_text(
        "movieId,title,genres\n"
        "1,The Matrix (1999),Action|Sci-Fi\n"
        "2,Toy Story (1995),Animation|Children|Comedy\n"
        "3,Heat (1995),Action|Crime|Thriller\n"
    )

    ratings_file = tmp_path / "ratings.json"
    ratings_data = [
        {"id": "r1", "user_id": "u1", "movie_id": 1, "rating": 5.0, "timestamp": "2025-10-25T00:00:00"},
        {"id": "r2", "user_id": "u2", "movie_id": 1, "rating": 4.0, "timestamp": "2025-10-25T00:00:00"},
        {"id": "r3", "user_id": "u3", "movie_id": 2, "rating": 3.5, "timestamp": "2025-10-25T00:00:00"}
    ]
    ratings_file.write_text(json.dumps(ratings_data))

    return movie_dir, ratings_file

def test_load_movies(setup_movie_data):
    movie_dir, _ = setup_movie_data
    repo = MoviesRepository(movies_dir=movie_dir)
    assert repo.movies_df is not None
    assert len(repo.movies_df) == 3
    assert list(repo.movies_df.columns) == ["movieId", "title", "genres", "year"]

def test_extract_year(setup_movie_data):
    movie_dir, _ = setup_movie_data
    repo = MoviesRepository(movies_dir=movie_dir)

    assert repo._extract_year("Toy Story (1995)") == 1995
    assert repo._extract_year("More Complicated Movie Title (That Even Has Brackets) (1994)") == 1994
    assert repo._extract_year("Very Real Movie With No Year: 100 Emoji") is None

def test_get_by_id(setup_movie_data):
    movie_dir, _ = setup_movie_data
    repo = MoviesRepository(movies_dir=movie_dir)

    movie = repo.get_by_id(1)
    assert movie is not None
    assert movie["movieId"] == 1
    assert movie["title"] == "The Matrix (1999)"
    assert set(movie["genres"]) == {"Action", "Sci-Fi"}

def test_get_by_id_not_found(setup_movie_data):
    movie_dir, _ = setup_movie_data
    repo = MoviesRepository(movies_dir=movie_dir)

    movie = repo.get_by_id(999)
    assert movie is None

def test_get_average_rating(setup_movie_data):
    movie_dir, ratings_file = setup_movie_data
    repo = MoviesRepository(movies_dir=movie_dir)

    avg = repo.get_average_rating(1, ratings_file)
    assert avg == 4.5

def test_get_average_rating_no_ratings(setup_movie_data):
    movie_dir, ratings_file = setup_movie_data
    repo = MoviesRepository(movies_dir=movie_dir)

    avg = repo.get_average_rating(3, ratings_file)
    assert avg is None

def test_search_movies(setup_movie_data):
    movie_dir, _ = setup_movie_data
    repo = MoviesRepository(movies_dir=movie_dir)

    results = repo.search("Matrix")
    assert len(results) == 1
    assert results[0]["title"] == "The Matrix (1999)"

def test_filter_by_genre(setup_movie_data):
    movie_dir, _ = setup_movie_data
    repo = MoviesRepository(movies_dir=movie_dir)

    results = repo.filter_by_genre("Action")
    assert len(results) == 2
    assert all("Action" in movie["genres"] for movie in results)

def test_get_genres(setup_movie_data):
    movie_dir, _ = setup_movie_data
    repo = MoviesRepository(movies_dir=movie_dir)

    genres = repo.get_genres()
    expected_genres = {"Action", "Animation", "Children", "Comedy", "Crime", "Sci-Fi", "Thriller"}
    assert set(genres) == expected_genres
    assert genres == sorted(genres)

def test_get_all_with_offset(setup_movie_data):
    movie_dir, _ = setup_movie_data
    repo = MoviesRepository(movies_dir=movie_dir)

    results = repo.get_all(limit=2, offset=1)
    assert len(results) == 2
    assert results[0]["movieId"] == 2
    assert results[1]["movieId"] == 3

def test_get_paginated_movies(setup_movie_data):
    movie_dir, _ = setup_movie_data
    repo = MoviesRepository(movies_dir=movie_dir)

    movies, total = repo.get_paginated_movies(page=1, page_size=2)
    assert len(movies) == 2
    assert total == 3

def test_genres_split_correctly(setup_movie_data):
    movie_dir, _ = setup_movie_data
    repo = MoviesRepository(movies_dir=movie_dir)

    movie = repo.get_by_id(2)
    assert movie is not None
    assert isinstance(movie["genres"], list)
    assert "Children" in movie["genres"]