"""Repository for storing user insights data."""

import json
from datetime import UTC, datetime
from pathlib import Path

from app.core.config import settings


class UserInsightsRepository:
    """Handle user insights stored in JSON."""

    def __init__(self, insights_file: str | None = None):
        """Initialize with path to insights JSON file."""
        if insights_file is None:
            insights_file = str(settings.DATA_DIR / "user_insights.json")
        self.insights_file = Path(insights_file)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create insights file if it doesn't exist."""
        try:
            if not self.insights_file.exists():
                self.insights_file.parent.mkdir(parents=True, exist_ok=True)
                self.insights_file.write_text("[]")
        except OSError as e:
            raise OSError(f"Failed to initialize insights file: {e}") from e

    def _read(self) -> list[dict]:
        """Read all insights."""
        try:
            content = self.insights_file.read_text()
            return json.loads(content)
        except (OSError, json.JSONDecodeError):
            return []

    def _write(self, data: list[dict]):
        """Write all insights to file."""
        try:
            with self.insights_file.open("w") as f:
                json.dump(data, f, indent=4, default=str)
        except OSError as e:
            raise OSError(f"Failed to write insights file: {e}") from e

    def get_by_user_id(self, user_id: str) -> dict | None:
        """Get insights for a specific user."""
        data = self._read()
        return next((item for item in data if item["user_id"] == user_id), None)

    def save(self, insights_data: dict) -> dict:
        """Save or update insights for a user."""
        data = self._read()
        user_id = insights_data["user_id"]

        # Remove existing insights for this user
        data = [item for item in data if item["user_id"] != user_id]

        # Add timestamp if not present
        if "generated_at" not in insights_data:
            insights_data["generated_at"] = datetime.now(UTC).isoformat()

        data.append(insights_data)
        self._write(data)

        return insights_data

    def delete(self, user_id: str) -> bool:
        """Delete insights for a user."""
        data = self._read()
        new_data = [item for item in data if item["user_id"] != user_id]

        if len(new_data) < len(data):
            self._write(new_data)
            return True

        return False

    def exists(self, user_id: str) -> bool:
        """Check if insights exist for a user."""
        data = self._read()
        return any(item["user_id"] == user_id for item in data)

    def get_all(self) -> list[dict]:
        """Get all user insights."""
        return self._read()

    def save_data(self, data: list[dict]):
        """Overwrite the insights file with the given list."""
        self._write(data)
