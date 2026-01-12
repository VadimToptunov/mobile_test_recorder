"""
Test reporting and result aggregation

Unified test reporter supporting multiple formats:
- HTML reports
- Markdown reports
- PDF reports
- Allure reports
- JUnit XML
- Test execution analytics
"""

from .unified_reporter import UnifiedReporter, ReportFormat
from .junit_parser import JUnitParser
from .allure_generator import AllureGenerator
from .report_generator import (
    ReportGenerator,
    HTMLReportGenerator,
    MarkdownReportGenerator,
    JSONReportGenerator,
    TestSuiteResult,
    TestResult,
    TestStatus,
)

__all__ = [
    "UnifiedReporter",
    "ReportFormat",
    "JUnitParser",
    "AllureGenerator",
    "ReportGenerator",
    "HTMLReportGenerator",
    "MarkdownReportGenerator",
    "JSONReportGenerator",
    "TestSuiteResult",
    "TestResult",
    "TestStatus",
]
