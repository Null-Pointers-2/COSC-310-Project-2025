import pandas as pd
import pytest

from app.ml.feature_engineering.genome_processor import create_genome_features

def test_genome_duplicates(mocker):
    mock_logger = mocker.patch("app.ml.feature_engineering.genome_processor.logger")

    movies_df = pd.DataFrame({"movie_id": [100, 101]})
    genome_df = pd.DataFrame({
        "movie_id": [100, 101, 101],  # Duplicate movie_id
        "tag_id": [1, 1, 1],
        "relevance": [0.9, 0.4, 0.8]
    })

    result = create_genome_features(movies_df, genome_df)

    assert result.shape == (2, 1)
    assert result[0][0] == pytest.approx(0.9)
    assert result[1][0] == pytest.approx(0.6)
    