"""
Performance analyzer for mobile applications

Analyzes app performance metrics and identifies bottlenecks.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PerformanceMetrics:
    """Performance metrics for an app"""
    app_start_time: float  # seconds
    memory_usage: float  # MB
    cpu_usage: float  # percentage
    network_requests: int
    avg_request_time: float  # milliseconds
    fps: float  # frames per second
    battery_drain: float  # mAh/hour


@dataclass
class PerformanceIssue:
    """Performance issue detected"""
    category: str  # memory, cpu, network, rendering
    severity: str  # critical, high, medium, low
    description: str
    value: float
    threshold: float
    recommendation: str


class PerformanceAnalyzer:
    """
    Analyzes application performance
    """

    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.issues: List[PerformanceIssue] = []

    def analyze_metrics(self, metrics: PerformanceMetrics, profile_name: str = "default") -> List[PerformanceIssue]:
        """
        Analyze performance metrics

        Args:
            metrics: Performance metrics to analyze
            profile_name: Profile name for tracking

        Returns:
            List of performance issues
        """
        self.metrics[profile_name] = metrics
        self.issues = []

        # Check app start time
        if metrics.app_start_time > 3.0:
            self.issues.append(PerformanceIssue(
                category="startup",
                severity="high",
                description="Slow app startup time",
                value=metrics.app_start_time,
                threshold=3.0,
                recommendation="Optimize initialization code and defer non-critical operations"
            ))

        # Check memory usage
        if metrics.memory_usage > 500:
            self.issues.append(PerformanceIssue(
                category="memory",
                severity="high",
                description="High memory usage",
                value=metrics.memory_usage,
                threshold=500,
                recommendation="Review memory leaks and optimize data structures"
            ))

        # Check CPU usage
        if metrics.cpu_usage > 80:
            self.issues.append(PerformanceIssue(
                category="cpu",
                severity="high",
                description="High CPU usage",
                value=metrics.cpu_usage,
                threshold=80,
                recommendation="Profile CPU-intensive operations and optimize algorithms"
            ))

        # Check network performance
        if metrics.avg_request_time > 1000:
            self.issues.append(PerformanceIssue(
                category="network",
                severity="medium",
                description="Slow network requests",
                value=metrics.avg_request_time,
                threshold=1000,
                recommendation="Optimize API calls, use caching, reduce payload size"
            ))

        # Check rendering performance
        if metrics.fps < 30:
            self.issues.append(PerformanceIssue(
                category="rendering",
                severity="high",
                description="Low frame rate",
                value=metrics.fps,
                threshold=30,
                recommendation="Optimize UI rendering, reduce overdraw, use hardware acceleration"
            ))

        # Check battery drain
        if metrics.battery_drain > 200:
            self.issues.append(PerformanceIssue(
                category="battery",
                severity="medium",
                description="High battery consumption",
                value=metrics.battery_drain,
                threshold=200,
                recommendation="Reduce background operations, optimize network usage"
            ))

        return self.issues

    def compare_profiles(self, profile1: str, profile2: str) -> Dict:
        """
        Compare two performance profiles

        Args:
            profile1: First profile name
            profile2: Second profile name

        Returns:
            Dictionary with comparison results
        """
        if profile1 not in self.metrics or profile2 not in self.metrics:
            return {}

        m1 = self.metrics[profile1]
        m2 = self.metrics[profile2]

        return {
            'startup_dif': m2.app_start_time - m1.app_start_time,
            'memory_dif': m2.memory_usage - m1.memory_usage,
            'cpu_dif': m2.cpu_usage - m1.cpu_usage,
            'fps_dif': m2.fps - m1.fps,
            'battery_diff': m2.battery_drain - m1.battery_drain,
        }

    def generate_report(self) -> str:
        """Generate performance analysis report"""
        report = "PERFORMANCE ANALYSIS REPORT\n"
        report += "=" * 80 + "\n\n"

        if not self.issues:
            report += "No performance issues detected.\n"
            return report

        # Group by category
        by_category = {}
        for issue in self.issues:
            if issue.category not in by_category:
                by_category[issue.category] = []
            by_category[issue.category].append(issue)

        for category, issues in by_category.items():
            report += f"\n{category.upper()} Issues ({len(issues)}):\n"
            report += "-" * 80 + "\n"

            for issue in issues:
                report += f"\n{issue.description} [{issue.severity.upper()}]\n"
                report += f"  Current: {issue.value:.2f}\n"
                report += f"  Threshold: {issue.threshold:.2f}\n"
                report += f"  Recommendation: {issue.recommendation}\n"

        report += "\n" + "=" * 80 + "\n"

        return report
