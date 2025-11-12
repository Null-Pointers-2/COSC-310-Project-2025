"""
Handles processing of MovieLens genome tag scores.
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def create_genome_features(movies_df: pd.DataFrame, genome_scores_df: pd.DataFrame) -> np.ndarray:
    """
    Create genome feature matrix from relevance scores.

    Assumes movies_df is already pre-filtered by the caller
    to ensure row alignment with other feature matrices.

    Each movie has 1128 genome tag relevance scores (0-1).
    """
    movie_ids = movies_df["movie_id"].unique()
    num_tags = genome_scores_df["tag_id"].max()

    logger.info("Creating genome matrix for %d movies x %d tags...", len(movie_ids), num_tags)

    movie_id_to_idx = {mid: idx for idx, mid in enumerate(movie_ids)}

    genome_matrix = np.zeros((len(movie_ids), num_tags), dtype=np.float32)

    relevant_genome_scores = genome_scores_df[genome_scores_df["movie_id"].isin(movie_id_to_idx)]

    for _, row in relevant_genome_scores.iterrows():
        movie_id = row["movie_id"]
        tag_id = int(row["tag_id"])
        relevance = row["relevance"]

        idx = movie_id_to_idx[movie_id]
        genome_matrix[idx, tag_id - 1] = relevance  # tag_id is 1-indexed

    return genome_matrix
