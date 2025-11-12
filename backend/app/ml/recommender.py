"""
Loads the pre-computed similarity matrix and
movie data to generate content-based recommendations.
"""

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class MovieRecommender:
    """
    Content-based movie recommender using pre-computed similarity.
    """

    def __init__(self, data_dir: str = "data/ml"):
        self.data_dir = Path(data_dir)
        self.movies_df: pd.DataFrame
        self.similarity_matrix: np.ndarray
        self.movie_id_to_idx: dict[int, int]
        self.idx_to_movie_id: dict[int, int]
        self.title_to_movie_id: dict[str, int]
        self.movie_id_to_title: dict[int, str]

        self.load_data()

    def load_data(self):
        """Load all necessary data artifacts."""
        logger.info("Loading recommender data...")

        movies_path = self.data_dir / "movies_clean.csv"
        if not movies_path.exists():
            raise FileNotFoundError(f"Missing {movies_path}. Run data_preprocessor.py.")
        self.movies_df = pd.read_csv(movies_path)

        self.movie_id_to_title = pd.Series(self.movies_df.title.values, index=self.movies_df.movie_id).to_dict()

        sim_matrix_path = self.data_dir / "similarity_matrix.npy"
        if not sim_matrix_path.exists():
            raise FileNotFoundError(f"Missing {sim_matrix_path}. Run similarity_matrix.py.")
        self.similarity_matrix = np.load(sim_matrix_path)

        mapping_path = self.data_dir / "movie_id_to_idx.json"
        if not mapping_path.exists():
            raise FileNotFoundError(f"Missing {mapping_path}. Run data_preprocessor.py.")
        with Path.open(mapping_path, "r") as f:
            self.movie_id_to_idx = json.load(f)

        self.movie_id_to_idx = {int(k): v for k, v in self.movie_id_to_idx.items()}

        self.idx_to_movie_id = {idx: mid for mid, idx in self.movie_id_to_idx.items()}
        self.title_to_movie_id = pd.Series(self.movies_df.movie_id.values, index=self.movies_df.title).to_dict()

    def get_recommendations(self, movie_title: str, n: int = 10) -> list[tuple[str, float]]:
        """
        Get the top N recommended movies for a given movie title.

        Args:
            movie_title: The exact title of the movie to base recommendations on.
            n: Number of recommendations to return (default 10).

        Returns:
            A list of tuples (recommended_movie_title, similarity_score),
            ordered from most to least similar.

        Raises:
            ValueError: If recommender data is not loaded.
            KeyError: If the given movie title is not found in the dataset.
        """
        if self.title_to_movie_id is None:
            raise ValueError("Recommender data not loaded.")

        movie_id = self.title_to_movie_id.get(movie_title)
        if movie_id is None:
            raise KeyError(f"Movie '{movie_title}' not found in recommender dataset.")

        recs_by_id = self.get_similar_by_id(movie_id, n)

        return [(self.movie_id_to_title.get(mid, "Unknown"), score) for mid, score in recs_by_id]

    def get_similar_by_id(self, movie_id: int, n: int = 10) -> list[tuple[int, float]]:
        """
        Get top N recommendations for a given movie ID.

        Args:
            movie_id: The MovieLens ID of the movie
            n: Number of recommendations to return

        Returns:
            A list of (movie_id, score) tuples.

        Raises:
            ValueError: If recommender data is not loaded or movie_id not found.
        """
        if self.movie_id_to_idx is None or self.similarity_matrix is None:
            raise ValueError("Recommender data not loaded.")

        if movie_id not in self.movie_id_to_idx:
            raise ValueError(f"Movie ID {movie_id} not found in recommender dataset.")

        movie_idx = self.movie_id_to_idx[movie_id]
        sim_scores = self.similarity_matrix[movie_idx]

        top_indices = np.argsort(sim_scores)[::-1]  # descending
        recommendations = []
        for idx in top_indices:
            if idx == movie_idx:
                continue  # skip itself
            rec_movie_id = self.idx_to_movie_id.get(idx)
            if rec_movie_id is None:
                continue
            recommendations.append((rec_movie_id, float(sim_scores[idx])))
            if len(recommendations) >= n:
                break

        return recommendations
