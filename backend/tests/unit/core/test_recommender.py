"""Unit tests for MovieRecommender class."""

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from app.ml.recommender import MovieRecommender


@pytest.fixture
def mock_data_files(tmp_path):
    data_dir = tmp_path / "ml"
    data_dir.mkdir()

    movies_csv = data_dir / "movies_clean.csv"
    movies_data = pd.DataFrame(
        {
            "movie_id": [1, 2, 3, 4, 5],
            "title": ["Movie 1", "Movie 2", "Movie 3", "Movie 4", "Movie 5"],
            "genres": ["Action|Sci-Fi", "Comedy", "Drama", "Action", "Sci-Fi"],
        },
    )
    movies_data.to_csv(movies_csv, index=False)

    similarity_matrix = np.array(
        [
            [1.0, 0.8, 0.3, 0.9, 0.7],
            [0.8, 1.0, 0.2, 0.6, 0.5],
            [0.3, 0.2, 1.0, 0.4, 0.3],
            [0.9, 0.6, 0.4, 1.0, 0.8],
            [0.7, 0.5, 0.3, 0.8, 1.0],
        ],
    )
    np.save(data_dir / "similarity_matrix.npy", similarity_matrix)

    movie_id_to_idx = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4}

    # Changed: Use json.dump instead of pickle.dump, and "w" mode instead of "wb"
    with Path.open(data_dir / "movie_id_to_idx.json", "w") as f:
        json.dump(movie_id_to_idx, f)

    return data_dir


def test_recommender_initialization(mock_data_files):
    recommender = MovieRecommender(data_dir=str(mock_data_files))

    assert recommender.movies_df is not None
    assert len(recommender.movies_df) == 5
    assert recommender.similarity_matrix is not None
    assert recommender.similarity_matrix.shape == (5, 5)
    assert len(recommender.movie_id_to_idx) == 5


def test_recommender_missing_movies_file(tmp_path):
    data_dir = tmp_path / "ml"
    data_dir.mkdir()

    with pytest.raises(FileNotFoundError, match=re.escape("movies_clean.csv")):
        MovieRecommender(data_dir=str(data_dir))


def test_recommender_missing_similarity_matrix(tmp_path):
    data_dir = tmp_path / "ml"
    data_dir.mkdir()

    movies_csv = data_dir / "movies_clean.csv"
    pd.DataFrame({"movie_id": [1], "title": ["Movie"], "genres": ["Action"]}).to_csv(movies_csv, index=False)

    with pytest.raises(FileNotFoundError, match=re.escape("similarity_matrix.npy")):
        MovieRecommender(data_dir=str(data_dir))


def test_get_similar_by_id_success(mock_data_files):
    recommender = MovieRecommender(data_dir=str(mock_data_files))

    similar = recommender.get_similar_by_id(movie_id=1, n=3)

    assert similar is not None
    assert len(similar) == 3

    movie_ids = [m[0] for m in similar]
    scores = [m[1] for m in similar]

    assert 1 not in movie_ids

    assert scores == sorted(scores, reverse=True)

    assert movie_ids[0] == 4


def test_get_similar_by_id_movie_not_found(mock_data_files):
    recommender = MovieRecommender(data_dir=str(mock_data_files))

    with pytest.raises(ValueError, match="Movie ID 999 not found"):
        recommender.get_similar_by_id(movie_id=999, n=3)


def test_get_similar_by_id_respects_limit(mock_data_files):
    recommender = MovieRecommender(data_dir=str(mock_data_files))

    similar = recommender.get_similar_by_id(movie_id=1, n=2)
    assert similar is not None
    assert len(similar) == 2


def test_get_recommendations_by_title_success(mock_data_files):
    recommender = MovieRecommender(data_dir=str(mock_data_files))

    recommendations = recommender.get_recommendations("Movie 1", n=3)

    assert recommendations is not None
    assert len(recommendations) == 3

    titles = [r[0] for r in recommendations]

    assert "Movie 1" not in titles


def test_get_recommendations_by_title_not_found(mock_data_files):
    recommender = MovieRecommender(data_dir=str(mock_data_files))

    with pytest.raises(KeyError, match="Movie 'definitely real movie bro trust me' not found"):
        recommender.get_recommendations("definitely real movie bro trust me", n=3)


def test_movie_id_to_title_mapping(mock_data_files):
    recommender = MovieRecommender(data_dir=str(mock_data_files))

    assert recommender.movie_id_to_title[1] == "Movie 1"
    assert recommender.movie_id_to_title[2] == "Movie 2"
    assert recommender.movie_id_to_title[5] == "Movie 5"


def test_title_to_movie_id_mapping(mock_data_files):
    recommender = MovieRecommender(data_dir=str(mock_data_files))

    assert recommender.title_to_movie_id["Movie 1"] == 1
    assert recommender.title_to_movie_id["Movie 2"] == 2
    assert recommender.title_to_movie_id["Movie 5"] == 5


def test_idx_to_movie_id_mapping(mock_data_files):
    recommender = MovieRecommender(data_dir=str(mock_data_files))

    assert recommender.idx_to_movie_id[0] == 1
    assert recommender.idx_to_movie_id[1] == 2
    assert recommender.idx_to_movie_id[4] == 5


def test_similarity_scores_are_floats(mock_data_files):
    recommender = MovieRecommender(data_dir=str(mock_data_files))

    similar = recommender.get_similar_by_id(movie_id=1, n=2)

    assert similar is not None
    for _movie_id, score in similar:
        assert isinstance(score, float)
        assert 0 <= score <= 1


def test_recommendations_exclude_query_movie(mock_data_files):
    recommender = MovieRecommender(data_dir=str(mock_data_files))

    similar = recommender.get_similar_by_id(movie_id=1, n=10)

    assert similar is not None
    movie_ids = [m[0] for m in similar]
    assert 1 not in movie_ids


def test_get_similar_with_n_larger_than_dataset(mock_data_files):
    recommender = MovieRecommender(data_dir=str(mock_data_files))

    # We have 5 movies, asking for 10 should return 4 (excluding query movie)
    similar = recommender.get_similar_by_id(movie_id=1, n=10)

    assert similar is not None
    assert len(similar) == 4  # All other movies


def test_recommender_handles_invalid_movie_id_type(mock_data_files):
    recommender = MovieRecommender(data_dir=str(mock_data_files))

    with pytest.raises(ValueError, match="Movie ID -42 not found"):
        recommender.get_similar_by_id(movie_id=-42, n=3)


def test_similarity_matrix_symmetry(mock_data_files):
    recommender = MovieRecommender(data_dir=str(mock_data_files))

    matrix = recommender.similarity_matrix

    assert np.allclose(matrix, matrix.T)


def test_similarity_matrix_diagonal_ones(mock_data_files):
    recommender = MovieRecommender(data_dir=str(mock_data_files))

    matrix = recommender.similarity_matrix

    assert np.allclose(np.diag(matrix), 1.0)
