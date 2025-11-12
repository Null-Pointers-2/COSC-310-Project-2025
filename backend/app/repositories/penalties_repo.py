"""Repository for penalty data operations."""

from datetime import UTC, datetime
import json
from pathlib import Path
import uuid

from app.core.config import settings


class PenaltiesRepository:
    """Handle penalties stored in JSON."""

    def __init__(self, penalties_file: str | None = None):
        """Initialize with path to penalties JSON file."""
        if penalties_file is None:
            penalties_file = settings.PENALTIES_FILE
        self.penalties_file = Path(penalties_file)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create penalties file if it doesn't exist."""
        if not self.penalties_file.exists():
            self.penalties_file.parent.mkdir(parents=True, exist_ok=True)
            self.penalties_file.write_text("[]", encoding="utf-8")

    def _read(self) -> list[dict]:
        """Read all penalties from file."""
        try:
            with Path.open(self.penalties_file, encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            self.penalties_file.write_text("[]", encoding="utf-8")
            return []

    def _write(self, penalties: list[dict]):
        """Write all penalties to file."""
        with Path.open(self.penalties_file, "w", encoding="utf-8") as f:
            json.dump(penalties, f, indent=2, ensure_ascii=False)

    def get_all(self) -> list[dict]:
        """Get all penalties."""
        return self._read()

    def get_by_id(self, penalty_id: str) -> dict | None:
        """Get penalty by ID."""
        penalties = self._read()
        return next((p for p in penalties if p["id"] == penalty_id), None)

    def get_by_user(self, user_id: str) -> list[dict]:
        """Get all penalties for a user."""
        penalties = self._read()
        return [p for p in penalties if p["user_id"] == user_id]

    def get_active_by_user(self, user_id: str) -> list[dict]:
        """Get active penalties for a user."""
        penalties = self._read()
        return [p for p in penalties if p["user_id"] == user_id and p["status"] == "active"]

    def create(self, penalty_data: dict) -> dict:
        """Create a new penalty."""
        penalties = self._read()
        new_penalty = {
            "id": str(uuid.uuid4()),
            "user_id": penalty_data["user_id"],
            "reason": penalty_data["reason"],
            "description": penalty_data.get("description"),
            "status": "active",
            "issued_at": datetime.now(UTC).isoformat(),
            "resolved_at": None,
            "issued_by": penalty_data["issued_by"],
        }

        penalties.append(new_penalty)
        self._write(penalties)
        return new_penalty

    def update(self, penalty_id: str, penalty_data: dict) -> dict | None:
        """Update a penalty."""
        penalties = self._read()
        for i, p in enumerate(penalties):
            if p["id"] == penalty_id:
                updated = {**p, **penalty_data}
                penalties[i] = updated
                self._write(penalties)
                return updated
        return None

    def resolve(self, penalty_id: str) -> bool:
        """Mark a penalty as resolved."""
        penalties = self._read()
        for i, p in enumerate(penalties):
            if p["id"] == penalty_id:
                penalties[i]["status"] = "resolved"
                penalties[i]["resolved_at"] = datetime.now(UTC).isoformat()
                self._write(penalties)
                return True
        return False

    def delete(self, penalty_id: str) -> bool:
        """Delete a penalty."""
        penalties = self._read()
        new_penalties = [p for p in penalties if p["id"] != penalty_id]
        if len(new_penalties) == len(penalties):
            return False
        self._write(new_penalties)
        return True
