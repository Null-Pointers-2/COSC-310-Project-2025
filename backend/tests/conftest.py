"""
Pytest configuration - MUST set environment before ANY imports.
"""
import os
import sys
from pathlib import Path

os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-not-for-production"
