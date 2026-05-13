"""Pytest: add project root to sys.path for core.audit_core imports."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
