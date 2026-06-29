"""Regression tests for validate_no_hardcoded_secrets false-positive handling."""

from framework.security.config import validate_no_hardcoded_secrets


def test_placeholder_password_not_flagged():
    assert validate_no_hardcoded_secrets("password = 'wrong_password'", "x.py") == []
    assert validate_no_hardcoded_secrets('PASSWORD = "password"', "x.py") == []


def test_detection_regex_pattern_not_flagged():
    # A raw-string detection signature (as used by the security modules) is not
    # a hardcoded secret.
    code = 'SecretPattern("EC Private Key", r"-----BEGIN EC PRIVATE KEY-----")'
    assert validate_no_hardcoded_secrets(code, "framework/security/x.py") == []


def test_real_secret_still_flagged():
    assert validate_no_hardcoded_secrets('password = "S3cr3tL3ak3d99"', "x.py")
