"""
Loads the pre-computed combined feature matrix and calculates
the cosine similarity matrix.
"""
import numpy as np
from pathlib import Path

def compute_and_save_similarity(data_dir: Path):
    """
    Loads the feature matrix and computes the cosine similarity matrix.
    
    The feature matrix is assumed to be L2-normalized,
    so cosine similarity is just matrix multiplication.
    """
    feature_matrix_path = data_dir / 'combined_features.npy'
    output_path = data_dir / 'similarity_matrix.npy'
    
    if not feature_matrix_path.exists():
        raise FileNotFoundError(f"Missing {feature_matrix_path}. Run data_preprocessor.py.")

    features = np.load(feature_matrix_path)

    similarity_matrix = features @ features.T
    np.save(output_path, similarity_matrix)

if __name__ == "__main__":
    PROCESSED_DATA_PATH = Path("data/ml")
    compute_and_save_similarity(PROCESSED_DATA_PATH)