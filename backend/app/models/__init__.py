"""Database models."""

from app.models.user import User
from app.models.student import Student
from app.models.class_model import Class
from app.models.observation import Observation

__all__ = ["User", "Student", "Class", "Observation"]
