import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer

class MovieDataPreprocessor:
    """Preprocess MovieLens data for content-based recommendations."""

    def __init__(self, data_path: str = "backend/data/movies", output_dir: str = "backend/data/ml"):
        self.data_path = Path(data_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_movies(self):
        """Load movie data from CSV."""
        movies_path = self.data_path / "movies.csv"

        if not movies_path.exists():
            raise FileNotFoundError(f"Movies file not found at {movies_path}")
        
        movies_df = pd.read_csv(movies_path, encoding="utf-8")
        return movies_df

    def preprocess_genres(self, movies_df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess the genres column."""
        movies_df = movies_df.copy()
        movies_df['genres_processed'] = (movies_df['genres'].fillna('').str.replace('|', ' ', regex=False))
        movies_df = movies_df[movies_df['genres'] != '(no genres listed)']
        return movies_df

    def create_tfidf_matrix(self, movies_df: pd.DataFrame) -> tuple[np.ndarray, TfidfVectorizer, pd.DataFrame]:
        """Create TF-IDF matrix from genres."""
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(movies_df['genres_processed'])
        return tfidf_matrix, tfidf, movies_df

    def save_processed_data(self, movies_df: pd.DataFrame, tfidf_matrix: np.ndarray, tfidf_vectorizer: TfidfVectorizer):
        """Save processed data and vectorizer."""
        movies_df[['movieId', 'title', 'genres', 'genres_processed']].to_csv(self.output_dir / 'movies_clean.csv', index=False)

        np.save(self.output_dir / 'tfidf_matrix.npy', tfidf_matrix.toarray())

        with open(self.output_dir / 'tfidf_vectorizer.pkl', 'wb') as f:
            pickle.dump(tfidf_vectorizer, f)

        movie_id_to_idx = pd.Series(movies_df.index, index=movies_df['movieId']).to_dict()

        with open(self.output_dir / 'movie_id_to_idx.pkl', 'wb') as f:
            pickle.dump(movie_id_to_idx, f)

    def run_preprocessing(self):
        """Run full preprocessing pipeline."""
        movies_df = self.load_movies()
        movies_df = self.preprocess_genres(movies_df)
        tfidf_matrix, tfidf_vectorizer, movies_df = self.create_tfidf_matrix(movies_df)
        self.save_processed_data(movies_df, tfidf_matrix, tfidf_vectorizer)