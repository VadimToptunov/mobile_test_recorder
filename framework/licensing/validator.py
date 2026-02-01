"""
License Validation System

Simple, offline-first license validation with upgrade prompts.
"""

import hashlib
import hmac
import json
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any


class LicenseTier(Enum):
    """License tiers"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class License:
    """License information"""

    def __init__(
            self,
            key: str,
            tier: LicenseTier,
            email: str,
            expires_at: Optional[datetime] = None,
            features: Optional[list] = None
    ):
        self.key = key
        self.tier = tier
        self.email = email
        self.expires_at = expires_at
        self.features = features or self._default_features()

    def _default_features(self) -> list:
        """Default features per tier"""
        if self.tier == LicenseTier.ENTERPRISE:
            return ['ml_healing', 'cloud_devices', 'parallel_execution',
                    'distributed_execution', 'visual_testing', 'sso', 'audit_logs']
        elif self.tier == LicenseTier.PRO:
            return ['ml_healing', 'cloud_devices', 'parallel_execution']
        else:
            return []

    def is_valid(self) -> bool:
        """Check if license is still valid"""
        if not self.expires_at:
            return True  # Lifetime license
        return datetime.now() < self.expires_at

    def has_feature(self, feature: str) -> bool:
        """Check if license includes feature"""
        return feature in self.features

    def days_remaining(self) -> Optional[int]:
        """Days until expiration"""
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.now()
        return max(0, delta.days)


class LicenseValidator:
    """
    License validator with upgrade prompts

    Features:
    - Offline-first validation
    - Encrypted license keys
    - Feature flags
    - Upgrade prompts
    """

    # Secret for HMAC (in production: env variable)
    SECRET = os.getenv('LICENSE_SECRET', 'change-me-in-production')

    # Feature requirements
    FEATURE_TIERS = {
        'ml_healing': LicenseTier.PRO,
        'cloud_devices': LicenseTier.PRO,
        'parallel_execution': LicenseTier.PRO,
        'distributed_execution': LicenseTier.ENTERPRISE,
        'visual_testing': LicenseTier.ENTERPRISE,
        'sso': LicenseTier.ENTERPRISE,
        'audit_logs': LicenseTier.ENTERPRISE,
    }

    def __init__(self):
        self.license = self._load_license()
        self._show_welcome()

    def _load_license(self) -> License:
        """Load license from config"""
        license_file = Path.home() / '.observe' / 'license.json'

        if not license_file.exists():
            return License(
                key='FREE',
                tier=LicenseTier.FREE,
                email='',
            )

        try:
            with open(license_file) as f:
                data = json.load(f)

            # Validate license key
            if not self._verify_key(data['key'], data['email']):
                print("⚠️  Invalid license key, falling back to FREE tier")
                return License(key='FREE', tier=LicenseTier.FREE, email='')

            expires_at = None
            if data.get('expires_at'):
                expires_at = datetime.fromisoformat(data['expires_at'])

            return License(
                key=data['key'],
                tier=LicenseTier(data['tier']),
                email=data['email'],
                expires_at=expires_at,
                features=data.get('features')
            )
        except (OSError, json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"⚠️  Error loading license: {e}")
            return License(key='FREE', tier=LicenseTier.FREE, email='')

    def _verify_key(self, key: str, email: str) -> bool:
        """Verify license key using HMAC"""
        # Format: TIER-EMAIL_HASH-RANDOM
        try:
            parts = key.split('-')
            if len(parts) < 2:
                return False

            tier = parts[0]
            expected_hash = hmac.new(
                self.SECRET.encode(),
                f"{tier}:{email}".encode(),
                hashlib.sha256
            ).hexdigest()[:16]

            return parts[1] == expected_hash
        except (ValueError, TypeError, KeyError, IndexError):
            return False

    def _show_welcome(self):
        """Show license status on startup"""
        if self.license.tier == LicenseTier.FREE:
            return  # Silent for free tier

        days = self.license.days_remaining()
        if days is not None and days < 30:
            print(f"⚠️  License expires in {days} days")
            print(f"   Renew at: https://yoursite.com/renew")

    def check_feature(self, feature: str) -> bool:
        """
        Check if feature is available

        Args:
            feature: Feature name

        Returns:
            True if available, False with upgrade prompt if not
        """
        required_tier = self.FEATURE_TIERS.get(feature)

        if not required_tier:
            return True  # Feature doesn't require license

        # Check license validity
        if not self.license.is_valid():
            self._show_expired_prompt()
            return False

        # Check if license has feature
        if self.license.has_feature(feature):
            return True

        # Show upgrade prompt
        self._show_upgrade_prompt(feature, required_tier)
        return False

    def _show_upgrade_prompt(self, feature: str, required_tier: LicenseTier):
        """Show upgrade prompt with pricing"""
        feature_nice = feature.replace('_', ' ').title()

        print(f"\n⚡ {feature_nice} is a {required_tier.value.upper()} feature")
        print()

        if required_tier == LicenseTier.PRO:
            print("💎 Upgrade to PRO:")
            print("   • ML-powered test healing")
            print("   • Cloud device integration")
            print("   • Parallel test execution")
            print("   • Priority email support")
            print()
            print("   Price: $49/month or $499/year (save 15%)")
            print("   🎁 7-day free trial available!")
            print()
            print("   Upgrade: observe upgrade --trial")
            print("   Or visit: https://yoursite.com/pro")
        else:
            print("🏢 Upgrade to ENTERPRISE:")
            print("   • Everything in PRO, plus:")
            print("   • Distributed test execution")
            print("   • Visual regression testing")
            print("   • SSO & LDAP integration")
            print("   • Audit logs & compliance")
            print("   • Dedicated support & SLA")
            print("   • Custom integrations")
            print()
            print("   Contact sales: sales@yoursite.com")
            print("   Or visit: https://yoursite.com/enterprise")
        print()

    def _show_expired_prompt(self):
        """Show license expired message"""
        print("\n❌ Your license has expired")
        print()
        print("Renew your license at: https://yoursite.com/renew")
        print("Or contact support: support@yoursite.com")
        print()

    def activate(self, key: str, email: str) -> bool:
        """
        Activate license

        Args:
            key: License key
            email: Email address

        Returns:
            True if activation successful
        """
        if not self._verify_key(key, email):
            print("❌ Invalid license key")
            return False

        # Extract tier from key
        tier_str = key.split('-')[0].lower()
        tier = LicenseTier(tier_str)

        # Save license
        license_file = Path.home() / '.observe' / 'license.json'
        license_file.parent.mkdir(parents=True, exist_ok=True)

        license_data = {
            'key': key,
            'tier': tier.value,
            'email': email,
            'activated_at': datetime.now().isoformat(),
        }

        with open(license_file, 'w') as f:
            json.dump(license_data, f, indent=2)

        # Reload license
        self.license = self._load_license()

        print(f"✅ License activated successfully!")
        print(f"   Tier: {tier.value.upper()}")
        print(f"   Email: {email}")

        return True

    def deactivate(self):
        """Deactivate current license"""
        license_file = Path.home() / '.observe' / 'license.json'
        if license_file.exists():
            license_file.unlink()

        self.license = License(key='FREE', tier=LicenseTier.FREE, email='')
        print("✅ License deactivated")

    def status(self) -> Dict[str, Any]:
        """Get license status"""
        return {
            'tier': self.license.tier.value,
            'email': self.license.email,
            'valid': self.license.is_valid(),
            'expires_at': self.license.expires_at.isoformat() if self.license.expires_at else None,
            'days_remaining': self.license.days_remaining(),
            'features': self.license.features,
        }


# Global instance
_validator: Optional[LicenseValidator] = None


def get_validator() -> LicenseValidator:
    """Get global license validator instance"""
    global _validator
    if _validator is None:
        _validator = LicenseValidator()
    return _validator


def check_feature(feature: str) -> bool:
    """Check if feature is available (convenience function)"""
    return get_validator().check_feature(feature)


def is_pro() -> bool:
    """Check if user has PRO license"""
    validator = get_validator()
    return validator.license.tier in (LicenseTier.PRO, LicenseTier.ENTERPRISE)


def is_enterprise() -> bool:
    """Check if user has Enterprise license"""
    validator = get_validator()
    return validator.license.tier == LicenseTier.ENTERPRISE
