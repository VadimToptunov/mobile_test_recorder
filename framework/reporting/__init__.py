"""
Test reporting and result aggregation

Unified test reporter supporting multiple formats:
- HTML reports
- Allure reports
- JUnit XML
- Test execution analytics
"""

from .unified_reporter import UnifiedReporter, ReportFormat
from .junit_parser import JUnitParser
from .allure_generator import AllureGenerator

__all__ = [
    'UnifiedReporter',
    'ReportFormat',
    'JUnitParser',
    'AllureGenerator',
]
