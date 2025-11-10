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
        self.movies_df = None
        self.similarity_matrix = None
        self.movie_id_to_idx = None
        self.idx_to_movie_id = None
        self.title_to_movie_id = None
        
        self.load_data()
        
    def load_data(self):
        """Load all necessary data artifacts."""
        print("Loading recommender data...")
        
        movies_path = self.data_dir / 'movies_clean.csv'
        if not movies_path.exists():
            raise FileNotFoundError(f"Missing {movies_path}. Run data_preprocessor.py.")
        self.movies_df = pd.read_csv(movies_path)
        
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
        
        Args:
            movie_title: The exact title of the movie (e.g., "Toy Story (1995)")
            n: Number of recommendations to return
            
        Returns:
            A list of (title, score) tuples, or None if movie not found.
        """
        if movie_title not in self.title_to_movie_id:
            print(f"Error: Movie '{movie_title}' not found in database.")
            return None
            
        movie_id = self.title_to_movie_id[movie_title]
        
        if movie_id not in self.movie_id_to_idx:
            print(f"Error: Movie '{movie_title}' (ID: {movie_id}) not in feature matrix. Was it filtered?")
            return None
            
        movie_idx = self.movie_id_to_idx[movie_id]
        
        sim_scores = self.similarity_matrix[movie_idx]
        
        top_indices = np.argsort(sim_scores)[-(n+1):]
        
        top_indices = np.flip(top_indices)
        
        recommendations = []
        for idx in top_indices:
            if idx == movie_idx:
                continue  # Skip the input movie itself
                
            rec_movie_id = self.idx_to_movie_id.get(idx)
            if rec_movie_id is None:
                continue
                
            rec_title = self.movies_df[self.movies_df.movieId == rec_movie_id].title.values[0]
            score = sim_scores[idx]
            
            recommendations.append((rec_title, score))
            
            if len(recommendations) == n:
                break
                
        return recommendations