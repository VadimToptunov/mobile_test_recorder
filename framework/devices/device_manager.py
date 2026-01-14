"""Device management for CLI daemon."""

import subprocess
import json
from typing import List, Dict, Any, Optional


class DeviceManager:
    """Manage Android and iOS devices/simulators."""
    
    @staticmethod
    def list_android_devices() -> List[Dict[str, Any]]:
        """List Android devices via adb."""
        devices = []
        try:
            result = subprocess.run(
                ["adb", "devices", "-l"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            device_id = parts[0]
                            status = parts[1]
                            
                            # Get device info
                            name = DeviceManager._get_android_device_name(device_id)
                            api_level = DeviceManager._get_android_api_level(device_id)
                            
                            devices.append({
                                "id": device_id,
                                "name": name,
                                "platform": "android",
                                "status": "online" if status == "device" else status,
                                "api_level": api_level
                            })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return devices
    
    @staticmethod
    def list_ios_simulators() -> List[Dict[str, Any]]:
        """List iOS simulators via simctl."""
        devices = []
        try:
            result = subprocess.run(
                ["xcrun", "simctl", "list", "devices", "-j"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for runtime, device_list in data.get("devices", {}).items():
                    for device in device_list:
                        if device.get("isAvailable", False):
                            devices.append({
                                "id": device["udid"],
                                "name": device["name"],
                                "platform": "ios",
                                "status": device["state"].lower(),
                                "ios_version": runtime.split('.')[-1]
                            })
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass
        
        return devices
    
    @staticmethod
    def list_all_devices(platform: str = "all") -> List[Dict[str, Any]]:
        """List all devices based on platform filter."""
        devices = []
        
        if platform in ("all", "android"):
            devices.extend(DeviceManager.list_android_devices())
        
        if platform in ("all", "ios"):
            devices.extend(DeviceManager.list_ios_simulators())
        
        return devices
    
    @staticmethod
    def _get_android_device_name(device_id: str) -> str:
        """Get Android device model name."""
        try:
            result = subprocess.run(
                ["adb", "-s", device_id, "shell", "getprop", "ro.product.model"],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.stdout.strip() or device_id
        except:
            return device_id
    
    @staticmethod
    def _get_android_api_level(device_id: str) -> Optional[int]:
        """Get Android API level."""
        try:
            result = subprocess.run(
                ["adb", "-s", device_id, "shell", "getprop", "ro.build.version.sdk"],
                capture_output=True,
                text=True,
                timeout=2
            )
            return int(result.stdout.strip())
        except:
            return None
