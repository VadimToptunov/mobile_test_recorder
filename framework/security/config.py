"""
Security Configuration and Best Practices

Centralized security configuration for the Mobile Test Recorder framework.
"""

import hashlib
import logging
import os
import secrets
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security configuration and utilities"""

    # Sensitive environment variables that should never be logged
    SENSITIVE_ENV_VARS = {
        'PASSWORD', 'SECRET', 'KEY', 'TOKEN', 'API_KEY', 'ACCESS_KEY',
        'PRIVATE', 'CREDENTIAL', 'AUTH', 'BROWSERSTACK_ACCESS_KEY',
        'SAUCE_ACCESS_KEY', 'AWS_SECRET_ACCESS_KEY', 'SLACK_WEBHOOK_URL',
        'SMTP_PASSWORD', 'SESSION_ENCRYPTION_KEY', 'LICENSE_KEY'
    }

    # Build variants that should never have crypto export enabled
    PRODUCTION_BUILD_VARIANTS = {'release', 'production', 'prod'}

    def __init__(self):
        self.session_key = self._get_or_generate_session_key()
        self.test_password = os.environ.get('TEST_USER_PASSWORD', self._generate_secure_password())
        self.debug_mode = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'

    @staticmethod
    def _generate_secure_password(length: int = 16) -> str:
        """Generate a cryptographically secure random password"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))

        # Ensure password meets complexity requirements
        if not any(c.isupper() for c in password):
            password = password[0].upper() + password[1:]
        if not any(c.islower() for c in password):
            password = password[:-1] + 'a'
        if not any(c.isdigit() for c in password):
            password = password[:-1] + '9'

        return password

    @staticmethod
    def _get_or_generate_session_key() -> str:
        """Get or generate session encryption key"""
        key = os.environ.get('SESSION_ENCRYPTION_KEY')
        if key:
            return key

        # Generate temporary key (not persisted)
        key = secrets.token_hex(32)
        logger.warning(
            "No SESSION_ENCRYPTION_KEY found in environment. "
            "Generated temporary key. Set SESSION_ENCRYPTION_KEY in .env for production."
        )
        return key

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> str:
        """
        Hash password using SHA-256 (for testing only - use bcrypt/argon2 in production)

        Args:
            password: Plain text password
            salt: Optional salt (generated if not provided)

        Returns:
            Hashed password as hex string
        """
        if salt is None:
            salt = secrets.token_hex(16)

        combined = f"{salt}:{password}"
        hashed = hashlib.sha256(combined.encode()).hexdigest()
        return f"{salt}:{hashed}"

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            salt, expected_hash = hashed.split(':', 1)
            combined = f"{salt}:{password}"
            actual_hash = hashlib.sha256(combined.encode()).hexdigest()
            return secrets.compare_digest(expected_hash, actual_hash)
        except ValueError:
            return False

    @staticmethod
    def sanitize_for_logging(data: dict) -> dict:
        """Remove sensitive data from dict before logging"""
        sanitized = {}
        for key, value in data.items():
            key_upper = key.upper()
            is_sensitive = any(
                sensitive in key_upper
                for sensitive in SecurityConfig.SENSITIVE_ENV_VARS
            )

            if is_sensitive:
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = SecurityConfig.sanitize_for_logging(value)
            else:
                sanitized[key] = value

        return sanitized

    @staticmethod
    def validate_build_variant(variant: str, feature_name: str = "Crypto Export") -> bool:
        """
        Validate that security-sensitive features are not enabled in production builds

        Args:
            variant: Build variant name (e.g., 'debug', 'release', 'production')
            feature_name: Name of the feature being validated

        Returns:
            True if feature is allowed in this variant

        Raises:
            SecurityError if feature is not allowed in production
        """
        variant_lower = variant.lower()

        if variant_lower in SecurityConfig.PRODUCTION_BUILD_VARIANTS:
            raise SecurityError(
                f"{feature_name} is FORBIDDEN in production builds. "
                f"Current variant: {variant}. "
                f"This feature is only allowed in debug/test builds."
            )

        logger.info(f"{feature_name} enabled in {variant} build (non-production)")
        return True

    @staticmethod
    def check_file_permissions(file_path: Path) -> bool:
        """
        Check if file has secure permissions (not world-readable)

        Args:
            file_path: Path to file to check

        Returns:
            True if permissions are secure
        """
        if not file_path.exists():
            return True

        # Check if file is world-readable (on Unix-like systems)
        try:
            import stat
            mode = file_path.stat().st_mode

            # Check if others have read permission
            if mode & stat.S_IROTH:
                logger.warning(
                    f"File {file_path} is world-readable. "
                    f"Consider setting permissions to 600 or 640."
                )
                return False

            return True
        except Exception as e:
            logger.debug(f"Could not check file permissions: {e}")
            return True


class SecurityError(Exception):
    """Raised when a security constraint is violated"""
    pass


# Global security config instance
_security_config: Optional[SecurityConfig] = None


def get_security_config() -> SecurityConfig:
    """Get global security configuration instance"""
    global _security_config
    if _security_config is None:
        _security_config = SecurityConfig()
    return _security_config


def is_production_environment() -> bool:
    """Check if running in production environment"""
    env = os.environ.get('ENVIRONMENT', 'development').lower()
    ci = os.environ.get('CI', 'false').lower() == 'true'

    return env in ('production', 'prod') or (
            ci and os.environ.get('CI_ENVIRONMENT', '').lower() in ('production', 'prod')
    )


def validate_no_hardcoded_secrets(code: str, file_path: str = "unknown") -> list:
    """
    Scan code for potential hardcoded secrets

    Args:
        code: Source code to scan
        file_path: Path to file being scanned

    Returns:
        List of potential security issues found
    """
    import re

    issues = []

    # Patterns for common secrets
    patterns = {
        "Potential API Key": r'["\']([A-Za-z0-9]{32,})["\']',
        "Potential AWS Key": r'AKIA[0-9A-Z]{16}',
        "Potential Private Key": r'-----BEGIN (?:RSA|DSA|EC) PRIVATE KEY-----',
        "Hardcoded Password": r'password\s*=\s*["\'](?!.*env|.*config)[^"\']{8,}["\']',
        "Potential Token": r'token\s*=\s*["\'][A-Za-z0-9_-]{20,}["\']',
    }

    for issue_type, pattern in patterns.items():
        matches = re.finditer(pattern, code, re.IGNORECASE)
        for match in matches:
            # Skip common false positives
            if 'example' in match.group(0).lower():
                continue
            if 'test' in file_path.lower() and 'Test' in match.group(0):
                continue

            issues.append({
                'type': issue_type,
                'file': file_path,
                'line': code[:match.start()].count('\n') + 1,
                'snippet': match.group(0)[:50] + '...' if len(match.group(0)) > 50 else match.group(0)
            })

    return issues
