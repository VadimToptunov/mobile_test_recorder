"""
Security Module

Security scanning and vulnerability analysis for mobile applications.

Features:
- OWASP Mobile Top 10 2024 coverage
- Static Application Security Testing (SAST)
- Dynamic Application Security Testing (DAST)
- Hardcoded secrets detection (GitHub-level accuracy)
- Certificate pinning verification
- Binary security analysis
- Privacy compliance checking (GDPR, CCPA)
- Root/Jailbreak detection analysis
"""

from framework.security.scanner import (
    SecurityScanner,
    AndroidSecurityScanner,
    IOSSecurityScanner,
    SecurityScanResult,
    SecurityFinding,
    SeverityLevel,
    SecurityCheckCategory,
)

from framework.security.advanced_security import (
    AdvancedSecurityScanner,
    HardcodedSecretsScanner,
    CertificatePinningAnalyzer,
    BinarySecurityAnalyzer,
    PrivacyComplianceChecker,
    RootJailbreakAnalyzer,
    SecureCodingAnalyzer,
    SecurityVulnerability,
    OWASPMobileTop10,
    RiskLevel,
)

__all__ = [
    # Basic scanners
    "SecurityScanner",
    "AndroidSecurityScanner",
    "IOSSecurityScanner",
    "SecurityScanResult",
    "SecurityFinding",
    "SeverityLevel",
    "SecurityCheckCategory",
    # Advanced security (STEP 9)
    "AdvancedSecurityScanner",
    "HardcodedSecretsScanner",
    "CertificatePinningAnalyzer",
    "BinarySecurityAnalyzer",
    "PrivacyComplianceChecker",
    "RootJailbreakAnalyzer",
    "SecureCodingAnalyzer",
    "SecurityVulnerability",
    "OWASPMobileTop10",
    "RiskLevel",
]
