"""
Application configuration settings.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings."""
    
    # Base Directories
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"  
    STATIC_DIR: Path = BASE_DIR / "app" / "static"  
    ML_DIR: Path = DATA_DIR / "ml" 

    # User Data Files
    USERS_FILE: str = str(DATA_DIR / "users.csv")
    RATINGS_FILE: str = str(DATA_DIR / "ratings.json")
    RECOMMENDATIONS_FILE: str = str(DATA_DIR / "recommendations.json")
    PENALTIES_FILE: str = str(DATA_DIR / "penalties.json")
    WATCHLIST_FILE: str = str(DATA_DIR / "watchlist.json")
    
    # ML Artifacts 
    SIMILARITY_MATRIX_FILE: str = str(ML_DIR / "similarity_matrix.pkl")
    TFIDF_MATRIX_FILE: str = str(ML_DIR / "tfidf_matrix.npy")
    GENOME_MATRIX_FILE: str = str(ML_DIR / "genome_matrix.npy")
    COMBINED_MATRIX_FILE: str = str(ML_DIR / "combined_features.npy")
    MOVIE_INDEX_FILE: str = str(ML_DIR / "movie_id_to_idx.pkl")
    TFIDF_VECTORIZER_FILE: str = str(ML_DIR / "tfidf_vectorizer.pkl")
    
    # Static Movie Data Files 
    MOVIES_CSV: str = str(STATIC_DIR / "movies" / "movies.csv")
    GENOME_SCORES_CSV: str = str(STATIC_DIR / "movies" / "genome-scores.csv")
    GENOME_TAGS_CSV: str = str(STATIC_DIR / "movies" / "genome-tags.csv")
    LINKS_CSV: str = str(STATIC_DIR / "movies" / "links.csv")
    TAGS_CSV: str = str(STATIC_DIR / "movies" / "tags.csv")
    
    # Authentication
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 30
    MAX_PAGE_SIZE: int = 100

    # Rate Limiting
    MAX_RATINGS_PER_HOUR: int = 50
    MAX_RATINGS_PER_DAY: int = 250

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings() 