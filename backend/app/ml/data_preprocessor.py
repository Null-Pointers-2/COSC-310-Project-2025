"""
Orchestrates preprocessing of MovieLens data.
Combines genre-based TF-IDF features with genome tag relevance scores.
"""
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple
from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import TfidfVectorizer

from app.ml.feature_engineering import genre_processor, genome_processor

class MovieDataPreprocessor:
    """
    Orchestrates preprocessing of MovieLens data.
    """

    def __init__(self, data_path: str = "app/static/movies", output_dir: str = "data/ml", genre_weight: float = 0.3, genome_weight: float = 0.7):
        """
        Initialize preprocessor.
        
        Args:
            data_path: Path to movie CSV files
            output_dir: Path to save processed data
            genre_weight: Weight for genre features (0-1)
            genome_weight: Weight for genome features (0-1)
        """
        self.data_path = Path(data_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not (0 <= genre_weight <= 1) or not (0 <= genome_weight <= 1):
            raise ValueError("Weights must be between 0 and 1")
            
        total = genre_weight + genome_weight
        if total == 0:
            raise ValueError("Total weight cannot be zero")
            
        self.genre_weight = genre_weight / total
        self.genome_weight = genome_weight / total
        print(f"Using weights: Genre={self.genre_weight:.2f}, Genome={self.genome_weight:.2f}")

    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load movies, genome scores, and genome tags."""
        print("Loading data...")
        movies_path = self.data_path / "movies.csv"
        if not movies_path.exists():
            raise FileNotFoundError(f"Movies file not found at {movies_path}")
        movies_df = pd.read_csv(movies_path, encoding="utf-8")
        
        genome_scores_path = self.data_path / "genome-scores.csv"
        if not genome_scores_path.exists():
            raise FileNotFoundError(f"Genome scores not found at {genome_scores_path}")
        genome_scores_df = pd.read_csv(genome_scores_path, encoding="utf-8")
        
        genome_tags_path = self.data_path / "genome-tags.csv"
        if not genome_tags_path.exists():
            raise FileNotFoundError(f"Genome tags not found at {genome_tags_path}")
        genome_tags_df = pd.read_csv(genome_tags_path, encoding="utf-8")
        
        return movies_df, genome_scores_df, genome_tags_df

    def combine_features(self, genre_matrix: np.ndarray, genome_matrix: np.ndarray) -> np.ndarray:
        """
        Combine genre and genome features with configured weights.
        
        Args:
            genre_matrix: TF-IDF genre features (n_movies x n_genre_features)
            genome_matrix: Genome tag relevance scores
            
        Returns:
            Combined feature matrix
        """
        print("Combining genre and genome features...")
        print(f"  Genre matrix shape: {genre_matrix.shape}, dtype: {genre_matrix.dtype}")
        print(f"  Genome matrix shape: {genome_matrix.shape}, dtype: {genome_matrix.dtype}")
        
        if not isinstance(genre_matrix, np.ndarray):
            genre_matrix = np.array(genre_matrix.toarray() if hasattr(genre_matrix, 'toarray') else genre_matrix)
        if not isinstance(genome_matrix, np.ndarray):
            genome_matrix = np.array(genome_matrix.toarray() if hasattr(genome_matrix, 'toarray') else genome_matrix)
        
        # Normalize each feature set
        genre_normalized = normalize(genre_matrix, norm='l2', axis=1)
        genome_normalized = normalize(genome_matrix, norm='l2', axis=1)
        
        # Apply weights
        genre_weighted = genre_normalized * self.genre_weight
        genome_weighted = genome_normalized * self.genome_weight
        
        # Combine features
        combined = np.hstack([genre_weighted, genome_weighted])
        
        # Final normalization
        combined = normalize(combined, norm='l2', axis=1)
        
        return combined

    def save_processed_data(self, movies_df: pd.DataFrame, combined_matrix: np.ndarray, tfidf_vectorizer: 'TfidfVectorizer'):
        """Save all processed data and models."""
        
        movies_clean_path = self.output_dir / 'movies_clean.csv'
        movies_df[['movieId', 'title', 'genres']].to_csv(
            movies_clean_path, index=False
        )
        
        combined_path = self.output_dir / 'combined_features.npy'
        np.save(combined_path, combined_matrix)
        
        vectorizer_path = self.output_dir / 'tfidf_vectorizer.pkl'
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(tfidf_vectorizer, f)
        
        movie_id_to_idx = pd.Series(
            range(len(movies_df)),  
            index=movies_df['movieId']
        ).to_dict()
        
        mapping_path = self.output_dir / 'movie_id_to_idx.pkl'
        with open(mapping_path, 'wb') as f:
            pickle.dump(movie_id_to_idx, f)

    def run_preprocessing(self):
        """Run full preprocessing pipeline."""
        movies_df, genome_scores_df, _ = self.load_data()
        
        genre_matrix, tfidf_vectorizer, movies_filtered_df = genre_processor.create_genre_features(movies_df)
        
        genome_matrix = genome_processor.create_genome_features(movies_filtered_df, genome_scores_df)
        
        combined_matrix = self.combine_features(genre_matrix, genome_matrix)
        
        self.save_processed_data(movies_filtered_df, combined_matrix, tfidf_vectorizer)

if __name__ == "__main__":
    RAW_DATA_PATH = "app/static/movies"
    PROCESSED_DATA_PATH = "data/ml"
    
    preprocessor = MovieDataPreprocessor(
        data_path=RAW_DATA_PATH,
        output_dir=PROCESSED_DATA_PATH,
        genre_weight=0.3,
        genome_weight=0.7
    )
    preprocessor.run_preprocessing()