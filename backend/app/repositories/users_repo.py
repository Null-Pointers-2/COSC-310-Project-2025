"""Repository for user data operations."""
import csv
import json
from typing import List, Optional, Dict
from pathlib import Path

class UsersRepository:
    """Handle user data stored in CSV."""
    
    def __init__(self, users_file: str = "data/users.csv"):
        """Initialize with path to users CSV file."""
        self.users_file = Path(users_file)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create users file with headers if it doesn't exist."""
        # TODO: Implement
        pass
    
    def get_all(self) -> List[Dict]:
        """Get all users."""
        # TODO: Read from CSV and return list of dicts
        pass
    
    def get_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        # TODO: Implement
        pass
    
    def get_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username."""
        # TODO: Implement
        pass
    
    def get_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        # TODO: Implement
        pass
    
    def create(self, user_data: Dict) -> Dict:
        """Create a new user."""
        # TODO: Append to CSV file
        pass
    
    def update(self, user_id: str, user_data: Dict) -> Optional[Dict]:
        """Update user information."""
        # TODO: Read all, update one, write all back
        pass
    
    def delete(self, user_id: str) -> bool:
        """Delete a user."""
        # TODO: Read all, filter out one, write back
        pass