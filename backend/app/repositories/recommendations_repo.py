"""Repository for cached recommendations."""
import json
from typing import Optional, Dict, List
from pathlib import Path
from app.core.config import settings
from datetime import datetime, timezone, timedelta

class RecommendationsRepository:
    """Handle cached recommendations stored in JSON."""
    
    def __init__(self, recommendations_file: Optional[str] = None):
        """Initialize with path to recommendations JSON file."""
        if recommendations_file is None:
            recommendations_file = settings.RECOMMENDATIONS_FILE
        self.recommendations_file = Path(recommendations_file)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create recommendations file if it doesn't exist."""
        if not self.recommendations_file.exists():
            self.recommendations_file.parent.mkdir(parents=True, exist_ok=True)
            self.recommendations_file.write_text("{}", encoding="utf-8")
    
    def _read(self) -> Dict:
        """Read all cached recommendations."""
        try:
            with open(self.recommendations_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return {}
    
    def _write(self, recommendations: Dict):
        """Write all recommendations to file."""
        try:
            with open(self.recommendations_file, "w", encoding="utf-8") as f:
                json.dump(recommendations, f, indent=2, ensure_ascii=False)
        except OSError as e:
            raise Exception(f"Failed to write recommendations file: {e}") from e
    
    def get_for_user(self, user_id: str) -> Optional[Dict]:
        """Get cached recommendations for a user."""
        try:
            data = self._read()
        except Exception:
            return None
        return data.get(str(user_id))
    
    def save_for_user(self, user_id: str, recommendations: List[Dict]):
        """Save recommendations for a user."""
        data = self._read()
        data[str(user_id)] = {
            "recommendations": recommendations,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        self._write(data)
    
    def clear_for_user(self, user_id: str):
        """Clear cached recommendations for a user."""
        data = self._read()
        user_key = str(user_id)
        if user_key in data:
            del data[user_key]
            self._write(data)
    
    def is_fresh(self, user_id: str, max_age_hours: int = 24) -> bool:
        """Check if cached recommendations are still fresh."""
        cached = self.get_for_user(user_id)
        if not cached or "timestamp" not in cached:
            return False

        try:
            cached_time = datetime.fromisoformat(cached["timestamp"].replace("Z", "+00:00"))
            age = datetime.now(timezone.utc) - cached_time
            return age < timedelta(hours=max_age_hours)
        except (ValueError, KeyError):
            return False