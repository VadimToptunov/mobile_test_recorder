"""
Device management for multi-environment test execution
"""

from .device_manager import DeviceManager, Device, DeviceType, DeviceStatus
from .device_pool import DevicePool
from .providers import ADBProvider, InstrumentsProvider, BrowserStackProvider

__all__ = [
    'DeviceManager',
    'Device',
    'DeviceType',
    'DeviceStatus',
    'DevicePool',
    'ADBProvider',
    'InstrumentsProvider',
    'BrowserStackProvider',
]
