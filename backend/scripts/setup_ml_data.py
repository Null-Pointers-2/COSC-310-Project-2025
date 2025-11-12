#!/usr/bin/env python3
"""
Setup script to generate ML artifacts for the recommendation system.
Run this script after downloading the MovieLens datasets.

Usage:
    python scripts/setup_ml_data.py
"""

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml.data_preprocessor import MovieDataPreprocessor
from app.ml.similarity_matrix import compute_and_save_similarity


def main():
    """Generate all required ML artifacts."""
    logger.info("Movie Recommendation System - ML Data Setup")

    raw_data_path = Path("app/static/movies")
    processed_data_path = Path("data/ml")

    required_files = [
        raw_data_path / "movies.csv",
        raw_data_path / "genome-scores.csv",
        raw_data_path / "genome-tags.csv",
    ]

    missing_files = [f for f in required_files if not f.exists()]
    if missing_files:
        logger.error("Missing required data files:")
        for f in missing_files:
            logger.error("  - %s", f)
        logger.error("Please download the MovieLens dataset first. See README.md for instructions.")
        return 1

    try:
        logger.info("-" * 40)
        logger.info("Step 1: Preprocessing data and creating feature matrices...")
        logger.info("  Input: %s", raw_data_path)
        logger.info("  Output: %s", processed_data_path)

        preprocessor = MovieDataPreprocessor(
            data_path=str(raw_data_path),
            output_dir=str(processed_data_path),
            genre_weight=0.3,  # 30% weight for genre features
            genome_weight=0.7,  # 70% weight for genome tag features
        )

        preprocessor.run_preprocessing()
        logger.info("Feature matrices created successfully")

        logger.info("Step 2: Computing similarity matrix...")
        compute_and_save_similarity(processed_data_path)
        logger.info("Similarity matrix computed successfully")

        required_artifacts = [
            "movies_clean.csv",
            "combined_features.npy",
            "tfidf_vectorizer.pkl",
            "movie_id_to_idx.json",
            "similarity_matrix.npy",
        ]

        logger.info("Verifying artifacts...")
        all_exist = True
        for artifact in required_artifacts:
            artifact_path = processed_data_path / artifact
            if artifact_path.exists():
                size = artifact_path.stat().st_size / (1024 * 1024)  # Size in MB
                logger.info("  %s (%.2f MB)", artifact, size)
            else:
                logger.error("  %s (MISSING)", artifact)
                all_exist = False

        if not all_exist:
            logger.error("ERROR: Some artifacts are missing!")
            return 1

        logger.info("Setup completed successfully!")
        logger.info("The recommendation system is now ready to use.")
        logger.info("You can start the backend server with:")
        logger.info("  uvicorn app.main:app --reload")

    except FileNotFoundError:
        logger.exception("Required file missing: %s")
        return 1
    except OSError:
        logger.exception("OS error during setup: %s")
        return 1

    else:
        return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    sys.exit(main())
