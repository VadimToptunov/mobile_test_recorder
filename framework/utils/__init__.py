"""
Utilities package for the Mobile Test Recorder framework.

This package provides common utilities used across the framework:
- logger: Structured logging with Rich formatting
- validator: Input validation utilities
- sanitizer: Code identifier sanitization
- file_utils: File operation helpers
"""

from .logger import get_logger, setup_logging
from .validator import validate_path, validate_project_structure
from .sanitizer import sanitize_identifier, sanitize_class_name

__all__ = [
    "get_logger",
    "setup_logging",
    "validate_path",
    "validate_project_structure",
    "sanitize_identifier",
    "sanitize_class_name",
]
