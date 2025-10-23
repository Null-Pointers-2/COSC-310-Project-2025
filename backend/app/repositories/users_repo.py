"""Repository for user data operations."""
import csv
import json
from typing import List, Optional, Dict
from pathlib import Path
from uuid import uuid4

class UsersRepository:
    """Handle user data stored in CSV."""
    
    HEADERS = ["id", "username", "email", "hashed_password", "role", "created_at"]
    
    def __init__(self, users_file: str = "data/users.csv"):
        """Initialize with path to users CSV file."""
        self.users_file = Path(users_file)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create users file with headers if it doesn't exist."""
        if not self.users_file.exists():
            self.users_file.parent.mkdir(parents=True, exist_ok=True)
            with self.users_file.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.HEADERS)
                writer.writeheader()
    
    def get_all(self) -> List[Dict]:
        """Get all users."""
        with self.users_file.open("r", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def get_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        return next((u for u in self.get_all() if u["id"] == user_id), None)
    
    def get_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username."""
        return next((u for u in self.get_all() if u["username"] == username), None)
    
    def get_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        return next((u for u in self.get_all() if u["email"] == email), None)
    
    def create(self, user_data: Dict) -> Dict:
        """Create a new user."""
        user_data["id"] = str(uuid4())
        with self.users_file.open("a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writerow(user_data)
        return user_data
    
    def update(self, user_id: str, user_data: Dict) -> Optional[Dict]:
        """Update user information."""
        users = self.get_all()
        updated = False
        
        for i, user in enumerate(users):
            if user["id"] == user_id:
                # Merge the update data with existing user data
                users[i].update(user_data)
                users[i]["id"] = user_id
                updated = True
                break
        
        if not updated:
            return None
        
        # Write all users back to file
        with self.users_file.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writeheader()
            writer.writerows(users)
        
        return users[i] if updated else None
    
    def delete(self, user_id: str) -> bool:
        """Delete a user."""
        users = self.get_all()
        original_count = len(users)
        users = [u for u in users if u["id"] != user_id]
        
        if len(users) == original_count:
            return False  # User not found
        
        with self.users_file.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS)
            writer.writeheader()
            writer.writerows(users)
        
        return True