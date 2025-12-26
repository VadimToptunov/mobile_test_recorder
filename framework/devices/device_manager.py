"""
Unified device management interface

Provides abstraction over different device types:
- Local Android devices (ADB)
- Local iOS devices (instruments)
- Android emulators
- iOS simulators
- Cloud devices (BrowserStack, Sauce Labs, AWS Device Farm)
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import subprocess
import json


class DeviceType(Enum):
    """Type of device"""
    ANDROID_REAL = "android_real"
    ANDROID_EMULATOR = "android_emulator"
    IOS_REAL = "ios_real"
    IOS_SIMULATOR = "ios_simulator"
    BROWSERSTACK = "browserstack"
    SAUCELABS = "saucelabs"
    AWS_DEVICE_FARM = "aws_device_farm"


class DeviceStatus(Enum):
    """Device availability status"""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class Device:
    """Represents a physical or virtual device"""
    id: str  # Device ID (e.g., emulator-5554, udid, browserstack session)
    name: str  # Human-readable name
    type: DeviceType
    status: DeviceStatus
    platform: str  # "android" or "ios"
    platform_version: str  # OS version (e.g., "13.0", "iOS 16.0")
    
    # Hardware specs
    model: Optional[str] = None  # Device model (e.g., "Pixel 7", "iPhone 15")
    manufacturer: Optional[str] = None
    screen_size: Optional[str] = None  # e.g., "1080x2400"
    ram: Optional[int] = None  # MB
    
    # Capabilities
    capabilities: Dict[str, Any] = field(default_factory=dict)
    
    # Connection info
    provider: Optional[str] = None  # "adb", "instruments", "browserstack"
    host: Optional[str] = None  # For cloud devices
    
    # State
    last_seen: datetime = field(default_factory=datetime.now)
    current_app: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "status": self.status.value,
            "platform": self.platform,
            "platform_version": self.platform_version,
            "model": self.model,
            "manufacturer": self.manufacturer,
            "screen_size": self.screen_size,
            "ram": self.ram,
            "capabilities": self.capabilities,
            "provider": self.provider,
            "host": self.host,
            "last_seen": self.last_seen.isoformat(),
            "current_app": self.current_app,
        }
    
    def is_android(self) -> bool:
        """Check if device is Android"""
        return self.platform == "android"
    
    def is_ios(self) -> bool:
        """Check if device is iOS"""
        return self.platform == "ios"
    
    def is_emulator(self) -> bool:
        """Check if device is emulator/simulator"""
        return self.type in [DeviceType.ANDROID_EMULATOR, DeviceType.IOS_SIMULATOR]
    
    def is_cloud(self) -> bool:
        """Check if device is in cloud"""
        return self.type in [DeviceType.BROWSERSTACK, DeviceType.SAUCELABS, DeviceType.AWS_DEVICE_FARM]


class DeviceManager:
    """
    Unified device management
    
    Discovers, manages, and orchestrates devices across all providers.
    """
    
    def __init__(self):
        self.devices: List[Device] = []
        self._providers = {}
    
    def discover_all(self) -> List[Device]:
        """
        Discover all available devices from all providers
        
        Returns:
            List of discovered devices
        """
        print("Discovering devices...")
        self.devices = []
        
        # Discover Android devices via ADB
        android_devices = self._discover_android_devices()
        self.devices.extend(android_devices)
        print(f"  Found {len(android_devices)} Android device(s)")
        
        # Discover iOS devices via instruments
        ios_devices = self._discover_ios_devices()
        self.devices.extend(ios_devices)
        print(f"  Found {len(ios_devices)} iOS device(s)")
        
        print(f"\nTotal: {len(self.devices)} device(s) available")
        return self.devices
    
    def _discover_android_devices(self) -> List[Device]:
        """Discover Android devices and emulators via ADB"""
        devices = []
        
        try:
            # Check if adb is available
            result = subprocess.run(
                ['adb', 'devices', '-l'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print("  Warning: ADB not available")
                return devices
            
            # Parse adb devices output
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                if not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                device_id = parts[0]
                status_str = parts[1]
                
                # Parse device info
                info = {}
                for part in parts[2:]:
                    if ':' in part:
                        key, value = part.split(':', 1)
                        info[key] = value
                
                # Determine if emulator or real device
                is_emulator = device_id.startswith('emulator-')
                device_type = DeviceType.ANDROID_EMULATOR if is_emulator else DeviceType.ANDROID_REAL
                
                # Map ADB status to our status
                status_map = {
                    'device': DeviceStatus.AVAILABLE,
                    'offline': DeviceStatus.OFFLINE,
                    'unauthorized': DeviceStatus.ERROR,
                }
                status = status_map.get(status_str, DeviceStatus.UNKNOWN)
                
                # Get additional device info
                model = info.get('model', 'Unknown')
                
                # Get Android version
                version = self._get_android_version(device_id)
                
                device = Device(
                    id=device_id,
                    name=f"{model} ({device_id})",
                    type=device_type,
                    status=status,
                    platform="android",
                    platform_version=version,
                    model=model,
                    manufacturer=info.get('device', None),
                    provider="adb",
                    capabilities={
                        "adb_info": info
                    }
                )
                
                devices.append(device)
        
        except FileNotFoundError:
            print("  Warning: ADB not found in PATH")
        except Exception as e:
            print(f"  Error discovering Android devices: {e}")
        
        return devices
    
    def _get_android_version(self, device_id: str) -> str:
        """Get Android version for device"""
        try:
            result = subprocess.run(
                ['adb', '-s', device_id, 'shell', 'getprop', 'ro.build.version.release'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "Unknown"
    
    def _discover_ios_devices(self) -> List[Device]:
        """Discover iOS devices and simulators via instruments/simctl"""
        devices = []
        
        try:
            # Discover simulators via xcrun simctl
            result = subprocess.run(
                ['xcrun', 'simctl', 'list', 'devices', 'available', '--json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print("  Warning: simctl not available (not on macOS?)")
                return devices
            
            data = json.loads(result.stdout)
            
            for runtime, device_list in data.get('devices', {}).items():
                # Extract iOS version from runtime string
                # e.g., "com.apple.CoreSimulator.SimRuntime.iOS-16-0" -> "16.0"
                version_match = runtime.split('iOS-')
                version = version_match[1].replace('-', '.') if len(version_match) > 1 else "Unknown"
                
                for device_info in device_list:
                    if not device_info.get('isAvailable', False):
                        continue
                    
                    status = DeviceStatus.AVAILABLE if device_info.get('state') == 'Booted' else DeviceStatus.OFFLINE
                    
                    device = Device(
                        id=device_info['udid'],
                        name=device_info['name'],
                        type=DeviceType.IOS_SIMULATOR,
                        status=status,
                        platform="ios",
                        platform_version=version,
                        model=device_info['name'],
                        provider="simctl",
                        capabilities={
                            "simctl_info": device_info
                        }
                    )
                    
                    devices.append(device)
            
            # TODO: Discover real iOS devices via instruments
            # This requires more complex setup with libimobiledevice or idevice tools
            
        except FileNotFoundError:
            print("  Warning: xcrun not found (not on macOS?)")
        except json.JSONDecodeError as e:
            print(f"  Error parsing simctl output: {e}")
        except Exception as e:
            print(f"  Error discovering iOS devices: {e}")
        
        return devices
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """Get device by ID"""
        for device in self.devices:
            if device.id == device_id:
                return device
        return None
    
    def get_devices_by_platform(self, platform: str) -> List[Device]:
        """Get all devices for specific platform"""
        return [d for d in self.devices if d.platform == platform]
    
    def get_available_devices(self) -> List[Device]:
        """Get all available (not busy/offline) devices"""
        return [d for d in self.devices if d.status == DeviceStatus.AVAILABLE]
    
    def filter_devices(
        self,
        platform: Optional[str] = None,
        device_type: Optional[DeviceType] = None,
        min_version: Optional[str] = None,
        model: Optional[str] = None
    ) -> List[Device]:
        """
        Filter devices by criteria
        
        Args:
            platform: "android" or "ios"
            device_type: DeviceType enum
            min_version: Minimum OS version
            model: Device model name (partial match)
        
        Returns:
            Filtered list of devices
        """
        filtered = self.devices
        
        if platform:
            filtered = [d for d in filtered if d.platform == platform]
        
        if device_type:
            filtered = [d for d in filtered if d.type == device_type]
        
        if model:
            filtered = [d for d in filtered if model.lower() in (d.model or '').lower()]
        
        if min_version:
            # Simple version comparison (works for most cases)
            filtered = [d for d in filtered if d.platform_version >= min_version]
        
        return filtered
    
    def list_devices(self, verbose: bool = False) -> None:
        """Print device list"""
        if not self.devices:
            print("No devices found.")
            return
        
        print(f"\n{'='*80}")
        print(f"Available Devices ({len(self.devices)})")
        print(f"{'='*80}\n")
        
        # Group by platform
        android_devices = [d for d in self.devices if d.is_android()]
        ios_devices = [d for d in self.devices if d.is_ios()]
        
        if android_devices:
            print("ANDROID:")
            for device in android_devices:
                status_icon = {
                    DeviceStatus.AVAILABLE: "✓",
                    DeviceStatus.BUSY: "⚠",
                    DeviceStatus.OFFLINE: "✗",
                    DeviceStatus.ERROR: "✗",
                    DeviceStatus.UNKNOWN: "?"
                }[device.status]
                
                type_label = "Emulator" if device.is_emulator() else "Device"
                print(f"  {status_icon} [{device.id}] {device.name}")
                print(f"      Type: {type_label} | Version: {device.platform_version} | Status: {device.status.value}")
                
                if verbose and device.capabilities:
                    print(f"      Capabilities: {device.capabilities}")
                print()
        
        if ios_devices:
            print("iOS:")
            for device in ios_devices:
                status_icon = {
                    DeviceStatus.AVAILABLE: "✓",
                    DeviceStatus.BUSY: "⚠",
                    DeviceStatus.OFFLINE: "✗",
                    DeviceStatus.ERROR: "✗",
                    DeviceStatus.UNKNOWN: "?"
                }[device.status]
                
                type_label = "Simulator" if device.is_emulator() else "Device"
                print(f"  {status_icon} [{device.id}] {device.name}")
                print(f"      Type: {type_label} | Version: {device.platform_version} | Status: {device.status.value}")
                
                if verbose and device.capabilities:
                    print(f"      Capabilities: {device.capabilities}")
                print()
    
    def save_devices(self, output_path: Path):
        """Save device list to JSON"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "discovered_at": datetime.now().isoformat(),
            "total_devices": len(self.devices),
            "devices": [d.to_dict() for d in self.devices]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n✓ Device list saved to: {output_path}")

