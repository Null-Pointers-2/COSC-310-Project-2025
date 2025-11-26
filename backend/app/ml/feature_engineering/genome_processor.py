import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def create_genome_features(movies_df: pd.DataFrame, genome_scores_df: pd.DataFrame) -> np.ndarray:
    """
    Create genome feature matrix from relevance scores.
    """
    movie_ids = movies_df["movie_id"].unique()
    movie_ids = pd.Index(movie_ids).drop_duplicates()

    num_tags = genome_scores_df["tag_id"].max()
    logger.info("Creating genome matrix for %d movies x %d tags...", len(movie_ids), num_tags)

    relevant_genome_scores = genome_scores_df[genome_scores_df["movie_id"].isin(movie_ids)].copy()

    # Ensure no duplicate
    relevant_genome_scores = relevant_genome_scores.drop_duplicates(subset=["movie_id", "tag_id"], keep="first")

    genome_pivot = relevant_genome_scores.pivot_table(
        index="movie_id", columns="tag_id", values="relevance", fill_value=0.0
    )

    # Verify no duplicates
    if genome_pivot.index.duplicated().any():
        logger.warning("Found %d duplicate indices after pivot. Removing...", genome_pivot.index.duplicated().sum())
        genome_pivot = genome_pivot[~genome_pivot.index.duplicated(keep="first")]

    genome_pivot = genome_pivot.reindex(movie_ids, fill_value=0.0)

    return genome_pivot.to_numpy(dtype=np.float32)
