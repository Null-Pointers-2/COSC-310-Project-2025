"""
Loads the pre-computed similarity matrix and
movie data to generate content-based recommendations.
"""
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Tuple, Optional

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
        print("Loading recommender data...")
        
        movies_path = self.data_dir / 'movies_clean.csv'
        if not movies_path.exists():
            raise FileNotFoundError(f"Missing {movies_path}. Run data_preprocessor.py.")
        self.movies_df = pd.read_csv(movies_path)
        
        self.movie_id_to_title = pd.Series(
            self.movies_df.title.values, 
            index=self.movies_df.movieId
        ).to_dict()

        sim_matrix_path = self.data_dir / 'similarity_matrix.npy'
        if not sim_matrix_path.exists():
            raise FileNotFoundError(f"Missing {sim_matrix_path}. Run similarity_matrix.py.")
        self.similarity_matrix = np.load(sim_matrix_path)
        
        mapping_path = self.data_dir / 'movie_id_to_idx.pkl'
        if not mapping_path.exists():
            raise FileNotFoundError(f"Missing {mapping_path}. Run data_preprocessor.py.")
        with open(mapping_path, 'rb') as f:
            self.movie_id_to_idx = pickle.load(f)
            
        self.idx_to_movie_id = {idx: mid for mid, idx in self.movie_id_to_idx.items()}
        self.title_to_movie_id = pd.Series(self.movies_df.movieId.values, index=self.movies_df.title).to_dict()

    def get_recommendations(self, movie_title: str, n: int = 10) -> Optional[List[Tuple[str, float]]]:
        """
        Get top N recommendations for a given movie title.
        """
        if self.title_to_movie_id is None:
            raise ValueError("Recommender data not loaded.")
        
        movie_id = self.title_to_movie_id.get(movie_title)
        if movie_id is None:
            print(f"Error: Movie '{movie_title}' not found in recommender dataset.")
            return None

        recs_by_id = self.get_similar_by_id(movie_id, n)
        if recs_by_id is None:
            return None

        return [
            (self.movie_id_to_title.get(mid, "Unknown"), score)
            for mid, score in recs_by_id
        ]
    
    def get_similar_by_id(self, movie_id: int, n: int = 10) -> Optional[List[Tuple[int, float]]]:
        """
        Get top N recommendations for a given movie ID.
        
        Args:
            movie_id: The MovieLens ID of the movie
            n: Number of recommendations to return
            
        Returns:
            A list of (movie_id, score) tuples, or None if movie not found.
        """
        if self.movie_id_to_idx is None or self.similarity_matrix is None:
            raise ValueError("Recommender data not loaded.")

        if movie_id not in self.movie_id_to_idx:
            print(f"Warning: Movie ID {movie_id} not found in recommender dataset")
            return None

        movie_idx = self.movie_id_to_idx[movie_id]
        sim_scores = self.similarity_matrix[movie_idx]

        # Get top N most similar (excluding itself)
        top_indices = np.argsort(sim_scores)[::-1]  # descending
        recommendations = []
        for idx in top_indices:
            if idx == movie_idx:
                continue  # skip itself
            rec_movie_id = self.idx_to_movie_id.get(idx)
            if rec_movie_id is None:
                continue
            score = float(sim_scores[idx])
            recommendations.append((rec_movie_id, score))
            if len(recommendations) >= n:
                break

        return recommendations
