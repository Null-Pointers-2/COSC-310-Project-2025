"""
Handles all logic for processing and vectorizing movie genres.
"""

import logging

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)


def _preprocess_genres_df(movies_df: pd.DataFrame) -> pd.DataFrame:
    """
    Internal function to clean the genres column and filter out
    movies with no genre information.
    """
    movies_df = movies_df.copy()

    movies_df["genres_processed"] = movies_df["genres"].fillna("").str.replace("|", " ", regex=False)

    movies_df = movies_df[movies_df["genres"] != "(no genres listed)"].copy()

    logger.info("Filtered to %d movies with genres.", len(movies_df))
    return movies_df


def create_genre_features(
    movies_df: pd.DataFrame,
) -> tuple[np.ndarray, TfidfVectorizer, pd.DataFrame]:
    """
    Creates TF-IDF features from genres.

    Returns:
        - The TF-IDF matrix as a dense numpy array (np.ndarray)
        - The fitted TfidfVectorizer
        - The filtered movies_df with processed genres

    """
    logger.info("Creating genre TF-IDF features...")

    movies_processed_df = _preprocess_genres_df(movies_df)

    tfidf = TfidfVectorizer(stop_words="english", max_features=100)  # Limit features since genres are limited
    tfidf_matrix_sparse = tfidf.fit_transform(movies_processed_df["genres_processed"])

    tfidf_matrix = tfidf_matrix_sparse.toarray()  # type: ignore [attr-defined]

    logger.info("Created TF-IDF matrix with shape: %s", tfidf_matrix.shape)

    return tfidf_matrix, tfidf, movies_processed_df
