"""
Configuration package for the Mobile Test Recorder framework.

Centralized configuration management with environment variable support.
"""

from .settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
