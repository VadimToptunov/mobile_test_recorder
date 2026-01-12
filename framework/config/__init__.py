"""
Configuration package for the Mobile Test Recorder framework.

Centralized configuration management with environment variable support.
"""

from .settings import Settings, get_settings
from .config_manager import (
    ConfigManager,
    ObserveConfig,
    FrameworkConfig,
    DeviceConfig,
    MLConfig,
    IntegrationConfig,
)

__all__ = [
    "Settings",
    "get_settings",
    "ConfigManager",
    "ObserveConfig",
    "FrameworkConfig",
    "DeviceConfig",
    "MLConfig",
    "IntegrationConfig",
]
