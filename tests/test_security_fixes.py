"""
Regression tests for security-correctness fixes (refactor pass).

Pins the verified bugs: version-spec matching, substring crypto false
positives, and the fake DAST scanner that returned a false "secure".
"""

import tempfile
from pathlib import Path

from framework.security.dast_analyzer import APISecurityTester, DASTSeverity
from framework.security.sast_analyzer import CryptoAnalyzer
from framework.security.supply_chain import SupplyChainAnalyzer


class TestVersionMatches:
    """_version_matches must handle <=/>= and compare versions numerically."""

    def setup_method(self):
        self.sca = SupplyChainAnalyzer()

    def test_two_char_operators_not_dead(self):
        assert self.sca._version_matches("5.4", "<= 5.4") is True
        assert self.sca._version_matches("5.5", "<= 5.4") is False
        assert self.sca._version_matches("5.4", ">= 5.4") is True
        assert self.sca._version_matches("5.3", ">= 5.4") is False

    def test_numeric_not_lexical(self):
        # Lexical comparison would wrongly make "2.0" < "2.10" False.
        assert self.sca._version_matches("2.0", "< 2.10") is True
        assert self.sca._version_matches("2.10", "< 2.9") is False

    def test_plain_and_equals(self):
        assert self.sca._version_matches("1.2.3", "== 1.2.3") is True
        assert self.sca._version_matches("1.2.3", "1.2.3") is True


class TestWeakCryptoWordBoundary:
    """Weak-algorithm detection must not fire on substrings."""

    def _findings_for(self, source: str):
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(source)
            path = Path(f.name)
        try:
            return CryptoAnalyzer().analyze(path)
        finally:
            path.unlink()

    def test_no_false_positive_on_substring(self):
        # "describe", "nodes", "used" all contain "des"; must not be flagged.
        findings = self._findings_for("def describe_nodes():\n    return used_indexes\n")
        assert not any("des" in f.title.lower() or "DES" in f.description for f in findings)

    def test_real_weak_algo_still_flagged(self):
        findings = self._findings_for('cipher = Cipher.getInstance("DES")\n')
        assert findings, "a genuine DES usage should still be flagged"


def test_api_security_tester_reports_not_tested():
    """test_endpoint must not return [] (a false 'secure'); it reports an
    explicit INFO 'not tested' finding instead."""
    findings = APISecurityTester().test_endpoint("https://api.example.com/login", method="POST")
    assert len(findings) == 1
    assert findings[0].severity is DASTSeverity.INFO
    assert "not" in findings[0].title.lower()
