"""
Handles all logic for processing and vectorizing movie genres.
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Tuple

def _preprocess_genres_df(movies_df: pd.DataFrame) -> pd.DataFrame:
    """
    Internal function to clean the genres column and filter out
    movies with no genre information.
    """
    movies_df = movies_df.copy()
    
    # Convert pipe-separated genres to space-separated
    movies_df['genres_processed'] = (
        movies_df['genres']
        .fillna('')
        .str.replace('|', ' ', regex=False)
    )
    
    # Filter out movies with no genres listed
    movies_df = movies_df[movies_df['genres'] != '(no genres listed)'].copy()
    
    print(f"Filtered to {len(movies_df)} movies with genres.")
    return movies_df

def create_genre_features(movies_df: pd.DataFrame) -> Tuple[np.ndarray, TfidfVectorizer, pd.DataFrame]:
    """
    Creates TF-IDF features from genres.

    Returns:
        - The TF-IDF matrix (np.ndarray)
        - The fitted TfidfVectorizer
        - The filtered movies_df with processed genres
    """
    print("Creating genre TF-IDF features...")
    
    movies_processed_df = _preprocess_genres_df(movies_df)
    
    tfidf = TfidfVectorizer(stop_words='english', max_features=100) # Limit features since genres are limited
    tfidf_matrix = tfidf.fit_transform(movies_processed_df['genres_processed'])
    
    return tfidf_matrix.toarray(), tfidf, movies_processed_df