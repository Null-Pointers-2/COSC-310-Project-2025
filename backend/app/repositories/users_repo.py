"""Repository for user data operations."""

import csv
from pathlib import Path
from typing import ClassVar
from uuid import uuid4

from app.core.config import settings


class UsersRepository:
    """Handle user data stored in CSV."""

    HEADERS: ClassVar[list[str]] = ["id", "username", "email", "hashed_password", "role", "created_at"]

    def __init__(self, users_file: str | None = None):
        """Initialize with path to users CSV file."""
        if users_file is None:
            users_file = settings.USERS_FILE
        self.users_file = Path(users_file)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create users file with headers if it doesn't exist."""
        if not self.users_file.exists():
            self.users_file.parent.mkdir(parents=True, exist_ok=True)
            with self.users_file.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.HEADERS)
                writer.writeheader()

    def get_all(self) -> list[dict]:
        """Get all users."""
        with self.users_file.open("r", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def get_by_id(self, user_id: str) -> dict | None:
        """Get user by ID."""
        return next((u for u in self.get_all() if u["id"] == user_id), None)

    def get_by_username(self, username: str) -> dict | None:
        """Get user by username."""
        return next((u for u in self.get_all() if u["username"] == username), None)

    def get_by_email(self, email: str) -> dict | None:
        """Get user by email."""
        return next((u for u in self.get_all() if u["email"] == email), None)

    def create(self, user_data: dict) -> dict:
        """Create a new user."""
        user_copy = user_data.copy()

        if "id" not in user_copy or not user_copy["id"]:
            user_copy["id"] = str(uuid4())

        with self.users_file.open("a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writerow(user_copy)
        return user_copy

    def update(self, user_id: str, user_data: dict) -> dict | None:
        """Update user information."""
        users = self.get_all()
        updated = False
        updated_user = None

        for i, user in enumerate(users):
            if user["id"] == user_id:
                user.update(user_data)
                users[i] = user
                updated_user = user
                updated = True
                break

        if not updated:
            return None

        with self.users_file.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writeheader()
            writer.writerows(users)

        return updated_user

    def delete(self, user_id: str) -> bool:
        """Delete a user."""
        users = self.get_all()
        original_count = len(users)
        users = [u for u in users if u["id"] != user_id]

        if len(users) == original_count:
            return False

        with self.users_file.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writeheader()
            writer.writerows(users)

        return True

    def save_all(self, users: list[dict]):
        """Overwrite the CSV file with a new list of users."""
        with self.users_file.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writeheader()
            writer.writerows(users)
