#!/usr/bin/env python3
"""
Setup script to generate ML artifacts for the recommendation system.
Run this script after downloading the MovieLens datasets.

Usage:
    python scripts/setup_ml_data.py
"""

from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml.data_preprocessor import MovieDataPreprocessor
from app.ml.similarity_matrix import compute_and_save_similarity


def main():
    """Generate all required ML artifacts."""
    print("Movie Recommendation System - ML Data Setup")
    print()

    raw_data_path = Path("app/static/movies")
    processed_data_path = Path("data/ml")

    required_files = [
        raw_data_path / "movies.csv",
        raw_data_path / "genome-scores.csv",
        raw_data_path / "genome-tags.csv",
    ]

    missing_files = [f for f in required_files if not f.exists()]
    if missing_files:
        print("ERROR: Missing required data files:")
        for f in missing_files:
            print(f"  - {f}")
        print()
        print("Please download the MovieLens dataset first.")
        print("See README.md for instructions.")
        return 1

    try:
        print("Step 1: Preprocessing data and creating feature matrices...")
        print(f"  Input: {raw_data_path}")
        print(f"  Output: {processed_data_path}")
        print()

        preprocessor = MovieDataPreprocessor(
            data_path=str(raw_data_path),
            output_dir=str(processed_data_path),
            genre_weight=0.3,  # 30% weight for genre features
            genome_weight=0.7,  # 70% weight for genome tag features
        )

        preprocessor.run_preprocessing()
        print("✓ Feature matrices created successfully")
        print()

        print("Step 2: Computing similarity matrix...")
        compute_and_save_similarity(processed_data_path)
        print("Similarity matrix computed successfully")
        print()

        required_artifacts = [
            "movies_clean.csv",
            "combined_features.npy",
            "tfidf_vectorizer.pkl",
            "movie_id_to_idx.pkl",
            "similarity_matrix.npy",
        ]

        print("Verifying artifacts...")
        all_exist = True
        for artifact in required_artifacts:
            artifact_path = processed_data_path / artifact
            if artifact_path.exists():
                size = artifact_path.stat().st_size / (1024 * 1024)  # Size in MB
                print(f"   {artifact} ({size:.2f} MB)")
            else:
                print(f"   {artifact} (MISSING)")
                all_exist = False

        if not all_exist:
            print()
            print("ERROR: Some artifacts are missing!")
            return 1

        print()
        print("Setup completed successfully!")
        print()
        print("The recommendation system is now ready to use.")
        print("You can start the backend server with:")
        print("  uvicorn app.main:app --reload")
        print()

        return 0

    except Exception as e:
        print()
        print("ERROR: Setup failed!")
        print(f"{type(e).__name__}: {e}")
        print()
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
