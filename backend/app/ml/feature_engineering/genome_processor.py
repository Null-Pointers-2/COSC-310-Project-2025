"""
Handles processing of MovieLens genome tag scores.
"""

import numpy as np
import pandas as pd


def create_genome_features(movies_df: pd.DataFrame, genome_scores_df: pd.DataFrame) -> np.ndarray:
    """
    Create genome feature matrix from relevance scores.

    Assumes movies_df is already pre-filtered by the caller
    to ensure row alignment with other feature matrices.

    Each movie has 1128 genome tag relevance scores (0-1).
    """
    movie_ids = movies_df["movieId"].unique()
    num_tags = genome_scores_df["tagId"].max()

    print(f"Creating genome matrix for {len(movie_ids)} movies x {num_tags} tags...")

    movie_id_to_idx = {mid: idx for idx, mid in enumerate(movie_ids)}

    genome_matrix = np.zeros((len(movie_ids), num_tags), dtype=np.float32)

    relevant_genome_scores = genome_scores_df[genome_scores_df["movieId"].isin(movie_id_to_idx)]

    for _, row in relevant_genome_scores.iterrows():
        movie_id = row["movieId"]
        tag_id = int(row["tagId"])
        relevance = row["relevance"]

        idx = movie_id_to_idx[movie_id]
        genome_matrix[idx, tag_id - 1] = relevance  # tagId is 1-indexed

    return genome_matrix
