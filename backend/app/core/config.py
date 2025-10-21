"""
Application configuration settings.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # File Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "app" / "data"
    MOVIES_DIR: Path = BASE_DIR / "movies"
    
    # Authentication
    SECRET_KEY: str = "Rty5xj1vTBBgOD3WY+061cnFeuFVg4MFSbk+MC+sBOb0/0MXNdLScda4t9RmN/VJ" # From jwtsecrets, obviously this should be in a .env for a production project
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    USERS_FILE: str = str(BASE_DIR / "data" / "users.csv")
    RATINGS_FILE: str = str(DATA_DIR / "ratings.json")
    RECOMMENDATIONS_FILE: str = str(DATA_DIR / "recommendations.json")
    PENALTIES_FILE: str = str(DATA_DIR / "penalties.json")
    WATCHLIST_FILE: str = str(DATA_DIR / "watchlist.json")
    SIMILARITY_MATRIX_FILE: str = str(DATA_DIR / "similarity_matrix.pkl") # TODO: doesn't actually exist yet
    
    # Movie Data Files
    MOVIES_CSV: str = str(MOVIES_DIR / "movie.csv")
    GENOME_SCORES_CSV: str = str(MOVIES_DIR / "genome_scores.csv")
    GENOME_TAGS_CSV: str = str(MOVIES_DIR / "genome_tags.csv")
    LINKS_CSV: str = str(MOVIES_DIR / "link.csv")
    TAGS_CSV: str = str(MOVIES_DIR / "tag.csv")
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 30
    MAX_PAGE_SIZE: int = 100
    
    # Rate Limiting
    MAX_RATINGS_PER_HOUR: int = 50
    MAX_RATINGS_PER_DAY: int = 250
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://frontend:3000",
    ]

settings = Settings()