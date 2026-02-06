"""
Decompilation and Reverse Engineering Module

Binary analysis and decompilation for mobile applications.

Features:
- APK decompilation and analysis
- IPA analysis
- DEX file analysis
- Native library analysis
- String extraction
- Resource extraction
- Manifest analysis
- Smali code analysis
- Binary protection detection
"""

import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
import xml.etree.ElementTree as ET


class ProtectionType(Enum):
    """Binary protection types"""
    OBFUSCATION = "obfuscation"
    ROOT_DETECTION = "root_detection"
    JAILBREAK_DETECTION = "jailbreak_detection"
    EMULATOR_DETECTION = "emulator_detection"
    DEBUG_DETECTION = "debug_detection"
    TAMPER_DETECTION = "tamper_detection"
    CERTIFICATE_PINNING = "certificate_pinning"
    CODE_SIGNING = "code_signing"
    ENCRYPTION = "encryption"
    PACKING = "packing"


class BinaryType(Enum):
    """Binary types"""
    APK = "apk"
    AAB = "aab"
    IPA = "ipa"
    DEX = "dex"
    SO = "so"
    DYLIB = "dylib"


@dataclass
class StringFinding:
    """Extracted string finding"""
    value: str
    location: str
    category: str  # url, api_key, password, etc.
    confidence: float


@dataclass
class DecompileResult:
    """Decompilation result"""
    binary_type: BinaryType
    binary_path: str
    output_dir: str
    package_name: Optional[str]
    version_name: Optional[str]
    version_code: Optional[int]
    min_sdk: Optional[int]
    target_sdk: Optional[int]
    permissions: List[str]
    activities: List[str]
    services: List[str]
    receivers: List[str]
    providers: List[str]
    native_libs: List[str]
    strings: List[StringFinding]
    protections: List[ProtectionType]
    hashes: Dict[str, str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "binary_type": self.binary_type.value,
            "binary_path": self.binary_path,
            "output_dir": self.output_dir,
            "package_name": self.package_name,
            "version_name": self.version_name,
            "version_code": self.version_code,
            "min_sdk": self.min_sdk,
            "target_sdk": self.target_sdk,
            "permissions": self.permissions,
            "activities": self.activities,
            "services": self.services,
            "receivers": self.receivers,
            "providers": self.providers,
            "native_libs": self.native_libs,
            "strings": [{"value": s.value[:50], "category": s.category, "confidence": s.confidence} for s in self.strings],
            "protections": [p.value for p in self.protections],
            "hashes": self.hashes,
            "metadata": self.metadata,
        }


class APKDecompiler:
    """
    APK Decompilation and Analysis

    Decompiles Android APK files and extracts security-relevant information.
    """

    # Sensitive string patterns
    SENSITIVE_PATTERNS = {
        "url": r'https?://[^\s"\'<>]+',
        "ip_address": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        "api_key": r'(?:api[_-]?key|apikey|api_secret)["\s:=]+["\']?([\w\-]{20,})["\']?',
        "aws_key": r'AKIA[0-9A-Z]{16}',
        "google_api": r'AIza[0-9A-Za-z\-_]{35}',
        "firebase": r'[a-z0-9-]+\.firebaseio\.com',
        "password": r'(?:password|passwd|pwd)["\s:=]+["\']?([^\s"\']{4,})["\']?',
        "private_key": r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----',
        "jwt": r'eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+',
        "sql_query": r'(?:SELECT|INSERT|UPDATE|DELETE)\s+.+\s+(?:FROM|INTO|SET)',
    }

    # Root detection indicators
    ROOT_INDICATORS = [
        "su", "/system/app/Superuser", "/system/xbin/su",
        "com.noshufou.android.su", "com.thirdparty.superuser",
        "eu.chainfire.supersu", "com.koushikdutta.superuser",
        "com.topjohnwu.magisk", "RootBeer", "RootTools",
        "isRooted", "checkRoot", "detectRoot"
    ]

    # Emulator detection indicators
    EMULATOR_INDICATORS = [
        "generic", "goldfish", "vbox", "genymotion",
        "sdk_google_phone", "google_sdk", "Andy",
        "Emulator", "BlueStacks", "Nox", "isEmulator"
    ]

    # Debug detection indicators
    DEBUG_INDICATORS = [
        "isDebuggerConnected", "Debug.isDebuggerConnected",
        "Debugger", "JDWP", "waitForDebugger"
    ]

    # Obfuscation indicators
    OBFUSCATION_INDICATORS = [
        "proguard", "dexguard", "allatori", "zelix",
        "stringer", "dasho", "arxan"
    ]

    def decompile(self, apk_path: Path, output_dir: Optional[Path] = None) -> DecompileResult:
        """Decompile APK and extract information"""
        if not apk_path.exists():
            raise FileNotFoundError(f"APK not found: {apk_path}")

        # Create output directory
        if output_dir is None:
            output_dir = Path(tempfile.mkdtemp(prefix="apk_decompile_"))
        else:
            output_dir.mkdir(parents=True, exist_ok=True)

        # Calculate hashes
        hashes = self._calculate_hashes(apk_path)

        # Extract APK contents
        extract_dir = output_dir / "extracted"
        with zipfile.ZipFile(apk_path, 'r') as zf:
            zf.extractall(extract_dir)

        # Parse AndroidManifest
        manifest_info = self._parse_manifest(extract_dir / "AndroidManifest.xml")

        # Extract strings from DEX files
        strings = self._extract_strings(extract_dir)

        # Find native libraries
        native_libs = self._find_native_libs(extract_dir)

        # Detect protections
        protections = self._detect_protections(extract_dir, strings)

        # Try to decompile with apktool if available
        self._run_apktool(apk_path, output_dir / "apktool")

        # Try to decompile with jadx if available
        self._run_jadx(apk_path, output_dir / "jadx")

        return DecompileResult(
            binary_type=BinaryType.APK,
            binary_path=str(apk_path),
            output_dir=str(output_dir),
            package_name=manifest_info.get("package"),
            version_name=manifest_info.get("version_name"),
            version_code=manifest_info.get("version_code"),
            min_sdk=manifest_info.get("min_sdk"),
            target_sdk=manifest_info.get("target_sdk"),
            permissions=manifest_info.get("permissions", []),
            activities=manifest_info.get("activities", []),
            services=manifest_info.get("services", []),
            receivers=manifest_info.get("receivers", []),
            providers=manifest_info.get("providers", []),
            native_libs=native_libs,
            strings=strings,
            protections=protections,
            hashes=hashes,
            metadata={
                "file_size": apk_path.stat().st_size,
                "signing_info": self._get_signing_info(apk_path),
            }
        )

    def _calculate_hashes(self, file_path: Path) -> Dict[str, str]:
        """Calculate file hashes"""
        hashes = {}
        content = file_path.read_bytes()

        hashes["md5"] = hashlib.md5(content).hexdigest()
        hashes["sha1"] = hashlib.sha1(content).hexdigest()
        hashes["sha256"] = hashlib.sha256(content).hexdigest()

        return hashes

    def _parse_manifest(self, manifest_path: Path) -> Dict[str, Any]:
        """Parse AndroidManifest.xml"""
        info: Dict[str, Any] = {
            "permissions": [],
            "activities": [],
            "services": [],
            "receivers": [],
            "providers": [],
        }

        try:
            # Try parsing as binary XML first
            # If that fails, try as text XML
            try:
                tree = ET.parse(manifest_path)
                root = tree.getroot()
            except ET.ParseError:
                # Binary XML - would need axml parser
                return info

            ns = {'android': 'http://schemas.android.com/apk/res/android'}

            # Package info
            info["package"] = root.get("package")
            info["version_name"] = root.get('{http://schemas.android.com/apk/res/android}versionName')
            version_code = root.get('{http://schemas.android.com/apk/res/android}versionCode')
            info["version_code"] = int(version_code) if version_code else None

            # SDK versions
            uses_sdk = root.find('.//uses-sdk')
            if uses_sdk is not None:
                min_sdk = uses_sdk.get('{http://schemas.android.com/apk/res/android}minSdkVersion')
                target_sdk = uses_sdk.get('{http://schemas.android.com/apk/res/android}targetSdkVersion')
                info["min_sdk"] = int(min_sdk) if min_sdk else None
                info["target_sdk"] = int(target_sdk) if target_sdk else None

            # Permissions
            for perm in root.findall('.//uses-permission'):
                perm_name = perm.get('{http://schemas.android.com/apk/res/android}name')
                if perm_name:
                    info["permissions"].append(perm_name)

            # Components
            for activity in root.findall('.//activity'):
                name = activity.get('{http://schemas.android.com/apk/res/android}name')
                if name:
                    info["activities"].append(name)

            for service in root.findall('.//service'):
                name = service.get('{http://schemas.android.com/apk/res/android}name')
                if name:
                    info["services"].append(name)

            for receiver in root.findall('.//receiver'):
                name = receiver.get('{http://schemas.android.com/apk/res/android}name')
                if name:
                    info["receivers"].append(name)

            for provider in root.findall('.//provider'):
                name = provider.get('{http://schemas.android.com/apk/res/android}name')
                if name:
                    info["providers"].append(name)

        except (OSError, ET.ParseError):
            pass

        return info

    def _extract_strings(self, extract_dir: Path) -> List[StringFinding]:
        """Extract strings from DEX files"""
        strings = []

        # Find all DEX files
        dex_files = list(extract_dir.glob("*.dex"))

        for dex_file in dex_files:
            dex_strings = self._extract_dex_strings(dex_file)
            strings.extend(dex_strings)

        # Also search resource files
        res_dir = extract_dir / "res"
        if res_dir.exists():
            for xml_file in res_dir.rglob("*.xml"):
                try:
                    content = xml_file.read_text(errors='ignore')
                    for category, pattern in self.SENSITIVE_PATTERNS.items():
                        for match in re.finditer(pattern, content, re.IGNORECASE):
                            strings.append(StringFinding(
                                value=match.group(0),
                                location=str(xml_file),
                                category=category,
                                confidence=0.7,
                            ))
                except (OSError, UnicodeDecodeError):
                    pass

        return strings

    def _extract_dex_strings(self, dex_path: Path) -> List[StringFinding]:
        """Extract strings from a DEX file"""
        strings = []

        try:
            # Simple string extraction using strings-like approach
            content = dex_path.read_bytes()

            # Extract ASCII strings
            ascii_strings = re.findall(rb'[\x20-\x7e]{4,}', content)

            for s in ascii_strings:
                try:
                    decoded = s.decode('utf-8')
                    for category, pattern in self.SENSITIVE_PATTERNS.items():
                        if re.search(pattern, decoded, re.IGNORECASE):
                            strings.append(StringFinding(
                                value=decoded,
                                location=str(dex_path),
                                category=category,
                                confidence=0.8,
                            ))
                            break
                except UnicodeDecodeError:
                    pass

        except OSError:
            pass

        return strings

    def _find_native_libs(self, extract_dir: Path) -> List[str]:
        """Find native libraries"""
        libs = []

        lib_dir = extract_dir / "lib"
        if lib_dir.exists():
            for so_file in lib_dir.rglob("*.so"):
                libs.append(str(so_file.relative_to(extract_dir)))

        return libs

    def _detect_protections(
        self,
        extract_dir: Path,
        strings: List[StringFinding]
    ) -> List[ProtectionType]:
        """Detect binary protections"""
        protections = []

        # Get all string values for detection
        all_strings = {s.value.lower() for s in strings}

        # Check root detection
        if any(indicator.lower() in s for s in all_strings for indicator in self.ROOT_INDICATORS):
            protections.append(ProtectionType.ROOT_DETECTION)

        # Check emulator detection
        if any(indicator.lower() in s for s in all_strings for indicator in self.EMULATOR_INDICATORS):
            protections.append(ProtectionType.EMULATOR_DETECTION)

        # Check debug detection
        if any(indicator.lower() in s for s in all_strings for indicator in self.DEBUG_INDICATORS):
            protections.append(ProtectionType.DEBUG_DETECTION)

        # Check obfuscation
        if any(indicator.lower() in s for s in all_strings for indicator in self.OBFUSCATION_INDICATORS):
            protections.append(ProtectionType.OBFUSCATION)

        # Check for certificate pinning
        pinning_indicators = ["certificatepinner", "okhttp3.certificatepinner", "trustmanager"]
        if any(indicator in s for s in all_strings for indicator in pinning_indicators):
            protections.append(ProtectionType.CERTIFICATE_PINNING)

        return protections

    def _get_signing_info(self, apk_path: Path) -> Dict[str, Any]:
        """Get APK signing information"""
        info: Dict[str, Any] = {}

        try:
            # Try using apksigner if available
            result = subprocess.run(
                ["apksigner", "verify", "--print-certs", str(apk_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                info["signed"] = True
                info["details"] = result.stdout
            else:
                info["signed"] = False
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            info["signed"] = "unknown"

        return info

    def _run_apktool(self, apk_path: Path, output_dir: Path) -> bool:
        """Run apktool for decompilation"""
        try:
            result = subprocess.run(
                ["apktool", "d", "-f", "-o", str(output_dir), str(apk_path)],
                capture_output=True,
                timeout=300
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False

    def _run_jadx(self, apk_path: Path, output_dir: Path) -> bool:
        """Run jadx for Java decompilation"""
        try:
            result = subprocess.run(
                ["jadx", "-d", str(output_dir), str(apk_path)],
                capture_output=True,
                timeout=600
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False


class IPAAnalyzer:
    """
    IPA Analysis

    Analyzes iOS IPA files for security information.
    """

    # Sensitive string patterns (iOS specific)
    SENSITIVE_PATTERNS = {
        "url": r'https?://[^\s"\'<>]+',
        "api_key": r'(?:api[_-]?key|apikey|api_secret)["\s:=]+["\']?([\w\-]{20,})["\']?',
        "bundle_id": r'[a-zA-Z0-9\-\.]+\.[a-zA-Z0-9\-\.]+',
        "entitlement": r'<key>([^<]+)</key>',
    }

    # Jailbreak detection indicators
    JAILBREAK_INDICATORS = [
        "cydia", "substrate", "jailbreak", "JailBroken",
        "/Applications/Cydia.app", "/Library/MobileSubstrate",
        "/bin/bash", "/usr/sbin/sshd", "/etc/apt",
        "isJailbroken", "detectJailbreak"
    ]

    def analyze(self, ipa_path: Path, output_dir: Optional[Path] = None) -> DecompileResult:
        """Analyze IPA file"""
        if not ipa_path.exists():
            raise FileNotFoundError(f"IPA not found: {ipa_path}")

        if output_dir is None:
            output_dir = Path(tempfile.mkdtemp(prefix="ipa_analyze_"))
        else:
            output_dir.mkdir(parents=True, exist_ok=True)

        # Calculate hashes
        hashes = self._calculate_hashes(ipa_path)

        # Extract IPA
        extract_dir = output_dir / "extracted"
        with zipfile.ZipFile(ipa_path, 'r') as zf:
            zf.extractall(extract_dir)

        # Find the .app bundle
        payload_dir = extract_dir / "Payload"
        app_bundle = None
        if payload_dir.exists():
            for item in payload_dir.iterdir():
                if item.suffix == ".app":
                    app_bundle = item
                    break

        # Parse Info.plist
        info_plist = {}
        if app_bundle:
            plist_path = app_bundle / "Info.plist"
            if plist_path.exists():
                info_plist = self._parse_plist(plist_path)

        # Extract strings from binary
        strings = []
        if app_bundle:
            # Find main binary
            binary_name = info_plist.get("CFBundleExecutable", app_bundle.stem)
            binary_path = app_bundle / binary_name
            if binary_path.exists():
                strings = self._extract_binary_strings(binary_path)

        # Detect protections
        protections = self._detect_protections(strings)

        # Find frameworks
        frameworks = []
        if app_bundle:
            frameworks_dir = app_bundle / "Frameworks"
            if frameworks_dir.exists():
                for fw in frameworks_dir.iterdir():
                    if fw.suffix == ".framework":
                        frameworks.append(fw.name)

        return DecompileResult(
            binary_type=BinaryType.IPA,
            binary_path=str(ipa_path),
            output_dir=str(output_dir),
            package_name=info_plist.get("CFBundleIdentifier"),
            version_name=info_plist.get("CFBundleShortVersionString"),
            version_code=None,
            min_sdk=None,
            target_sdk=None,
            permissions=[],  # iOS uses entitlements
            activities=[],  # Not applicable to iOS
            services=[],
            receivers=[],
            providers=[],
            native_libs=frameworks,
            strings=strings,
            protections=protections,
            hashes=hashes,
            metadata={
                "bundle_name": info_plist.get("CFBundleName"),
                "minimum_os": info_plist.get("MinimumOSVersion"),
                "device_family": info_plist.get("UIDeviceFamily"),
                "ats_settings": info_plist.get("NSAppTransportSecurity", {}),
            }
        )

    def _calculate_hashes(self, file_path: Path) -> Dict[str, str]:
        """Calculate file hashes"""
        hashes = {}
        content = file_path.read_bytes()

        hashes["md5"] = hashlib.md5(content).hexdigest()
        hashes["sha1"] = hashlib.sha1(content).hexdigest()
        hashes["sha256"] = hashlib.sha256(content).hexdigest()

        return hashes

    def _parse_plist(self, plist_path: Path) -> Dict[str, Any]:
        """Parse Info.plist"""
        try:
            import plistlib
            with open(plist_path, 'rb') as f:
                return plistlib.load(f)
        except (OSError, Exception):
            return {}

    def _extract_binary_strings(self, binary_path: Path) -> List[StringFinding]:
        """Extract strings from Mach-O binary"""
        strings = []

        try:
            content = binary_path.read_bytes()

            # Extract ASCII strings
            ascii_strings = re.findall(rb'[\x20-\x7e]{4,}', content)

            for s in ascii_strings:
                try:
                    decoded = s.decode('utf-8')
                    for category, pattern in self.SENSITIVE_PATTERNS.items():
                        if re.search(pattern, decoded, re.IGNORECASE):
                            strings.append(StringFinding(
                                value=decoded,
                                location=str(binary_path),
                                category=category,
                                confidence=0.8,
                            ))
                            break
                except UnicodeDecodeError:
                    pass

        except OSError:
            pass

        return strings

    def _detect_protections(self, strings: List[StringFinding]) -> List[ProtectionType]:
        """Detect binary protections"""
        protections = []

        all_strings = {s.value.lower() for s in strings}

        # Check jailbreak detection
        if any(indicator.lower() in s for s in all_strings for indicator in self.JAILBREAK_INDICATORS):
            protections.append(ProtectionType.JAILBREAK_DETECTION)

        # Check for certificate pinning
        pinning_indicators = ["trustkit", "alamofire", "urlsessiondelegate"]
        if any(indicator in s for s in all_strings for indicator in pinning_indicators):
            protections.append(ProtectionType.CERTIFICATE_PINNING)

        return protections


class NativeLibAnalyzer:
    """
    Native Library Analyzer

    Analyzes native libraries (.so, .dylib) for security issues.
    """

    def analyze_so(self, so_path: Path) -> Dict[str, Any]:
        """Analyze ELF shared object"""
        info: Dict[str, Any] = {
            "path": str(so_path),
            "type": "elf",
            "protections": [],
            "imports": [],
            "exports": [],
        }

        try:
            content = so_path.read_bytes()

            # Check ELF magic
            if content[:4] != b'\x7fELF':
                return info

            # Check architecture
            arch_byte = content[4]
            info["arch"] = "32-bit" if arch_byte == 1 else "64-bit" if arch_byte == 2 else "unknown"

            # Check for security features using readelf if available
            try:
                result = subprocess.run(
                    ["readelf", "-d", str(so_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    # Check for RELRO
                    if "BIND_NOW" in result.stdout:
                        info["protections"].append("FULL_RELRO")
                    elif "RELRO" in result.stdout:
                        info["protections"].append("PARTIAL_RELRO")

                    # Check for stack canary
                    if "__stack_chk_fail" in result.stdout:
                        info["protections"].append("STACK_CANARY")

                # Check for PIE
                result = subprocess.run(
                    ["readelf", "-h", str(so_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if "DYN" in result.stdout:
                    info["protections"].append("PIE")

            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                pass

            # Extract strings for analysis
            strings = re.findall(rb'[\x20-\x7e]{4,}', content)
            info["string_count"] = len(strings)

        except OSError:
            pass

        return info


class Decompiler:
    """
    Comprehensive Decompiler

    Combines all decompilation and analysis capabilities.
    """

    def __init__(self):
        self.apk_decompiler = APKDecompiler()
        self.ipa_analyzer = IPAAnalyzer()
        self.native_analyzer = NativeLibAnalyzer()

    def analyze(self, binary_path: Path, output_dir: Optional[Path] = None) -> DecompileResult:
        """Analyze any supported binary"""
        suffix = binary_path.suffix.lower()

        if suffix == ".apk":
            return self.apk_decompiler.decompile(binary_path, output_dir)
        elif suffix == ".ipa":
            return self.ipa_analyzer.analyze(binary_path, output_dir)
        else:
            raise ValueError(f"Unsupported binary type: {suffix}")

    def export_report(self, result: DecompileResult, output_path: Path) -> None:
        """Export analysis report"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
