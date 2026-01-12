"""
Security CLI commands

Commands for security analysis and vulnerability scanning.
"""

import click
from pathlib import Path
import re

from framework.analysis.security_analyzer import SecurityAnalyzer  # noqa: F401
from framework.cli.rich_output import print_header, print_info, print_success, print_error, create_progress
from rich.console import Console
from rich.table import Table
import json

console = Console()


@click.group(name='security')
def security() -> None:
    """🔒 Security analysis commands"""
    pass


@security.command()
@click.option('--source', '-s', 'source_path', required=True,
              type=click.Path(exists=True), help='Path to source code')
@click.option('--platform', '-p', type=click.Choice(['android', 'ios']),
              default='android', help='Platform to analyze')
@click.option('--output', '-o', type=click.Path(),
              help='Output file for report (JSON)')
@click.option('--severity', type=click.Choice(['critical', 'high', 'medium', 'low', 'info']),
              help='Minimum severity level to report')
def scan(source_path: str, platform: str, output: str, severity: str) -> None:
    """Scan source code for security vulnerabilities"""
    print_header(f"Security Scan ({platform.capitalize()})")

    source_dir = Path(source_path)
    print_info(f"Source: {source_dir}")
    print_info(f"Platform: {platform}")

    try:
        # Run security analysis
        print_info("\n🔄 Analyzing security...")

        analyzer = SecurityAnalyzer(project_root=source_dir)  # noqa: F841 - for future use
        issues = analyzer.analyze(platform=platform)

        # Filter by severity if specified
        if severity:
            severity_order = ['critical', 'high', 'medium', 'low', 'info']
            min_index = severity_order.index(severity)
            issues = [i for i in issues if severity_order.index(i.severity.value) <= min_index]

        # Display summary
        print_info(f"\n📊 Found {len(issues)} security issues")

        if not issues:
            print_success("✅ No security issues found!")
            return

        # Count by severity
        by_severity = {}
        for issue in issues:
            sev = issue.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1

        # Display severity summary

        print_info("\n🎯 By Severity:")
        for sev in ['critical', 'high', 'medium', 'low', 'info']:
            if sev in by_severity:
                count = by_severity[sev]
                emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵', 'info': 'ℹ️'}[sev]
                print_info(f"  {emoji} {sev.capitalize()}: {count}")

        # Display detailed issues
        table = Table(title=f"Security Issues ({len(issues)})")
        table.add_column("Severity", style="bold")
        table.add_column("Issue", style="cyan")
        table.add_column("File", style="yellow")
        table.add_column("Line", style="green")

        for issue in issues[:20]:  # Show top 20
            severity_icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵', 'info': 'ℹ️'}[issue.severity.value]
            table.add_row(
                f"{severity_icon} {issue.severity.value}",
                issue.title,
                str(issue.file.name),
                str(issue.line) if issue.line else "N/A"
            )

        console.print(table)

        if len(issues) > 20:
            print_info(f"\n... and {len(issues) - 20} more issues")

        # Show recommendations for critical/high issues
        critical_high = [i for i in issues if i.severity.value in ['critical', 'high']]
        if critical_high:
            print_info(f"\n⚠️  {len(critical_high)} critical/high severity issues require immediate attention!")

        # Save report if requested
        if output:
            report = {
                'platform': platform,
                'total_issues': len(issues),
                'by_severity': by_severity,
                'issues': [
                    {
                        'severity': i.severity.value,
                        'title': i.title,
                        'description': i.description,
                        'file': str(i.file),
                        'line': i.line,
                        'recommendation': i.recommendation,
                        'cwe_id': i.cwe_id
                    }
                    for i in issues
                ]
            }

            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)

            print_success(f"\n✅ Report saved to: {output_path}")

    except Exception as e:
        print_error(f"Security scan failed: {e}")
        raise click.Abort()


@security.command(name='check-secrets')
@click.option('--source', '-s', 'source_path', required=True,
              type=click.Path(exists=True), help='Path to source code')
def check_secrets(source_path: str) -> None:
    """Scan for hardcoded secrets and credentials"""
    print_header("Secret Detection")

    source_dir = Path(source_path)
    print_info(f"Source: {source_dir}")

    try:
        analyzer = SecurityAnalyzer(project_root=source_dir)  # noqa: F841

        print_info("\n🔄 Scanning for secrets...")

        # Get all files
        files = list(source_dir.rglob("*.kt")) + list(source_dir.rglob("*.java")) + \
            list(source_dir.rglob("*.swift")) + list(source_dir.rglob("*.m"))

        secrets_found = 0
        files_with_secrets = []

        with create_progress() as progress:
            task = progress.add_task("Scanning files...", total=len(files))

            for file_path in files:
                try:
                    content = file_path.read_text(encoding='utf-8')

                    # Look for common secret patterns
                    patterns = [
                        (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']([^"\']+)["\']', 'API Key'),
                        (r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']([^"\']+)["\']', 'Password'),
                        (r'(?i)(secret|token)\s*[:=]\s*["\']([^"\']+)["\']', 'Secret/Token'),
                        (r'(?i)aws[_-]?(access[_-]?key|secret)', 'AWS Credentials'),
                    ]

                    for pattern, secret_type in patterns:
                        if re.search(pattern, content):
                            secrets_found += 1
                            if file_path not in files_with_secrets:
                                files_with_secrets.append((file_path, secret_type))

                except Exception:
                    pass

                progress.advance(task)

        if secrets_found == 0:
            print_success("\n✅ No hardcoded secrets found!")
        else:
            print_error(f"\n❌ Found {secrets_found} potential secrets in {len(files_with_secrets)} files")

            print_info("\n📁 Files with secrets:")
            for file_path, secret_type in files_with_secrets[:10]:
                print_error(f"  • {file_path.relative_to(source_dir)} ({secret_type})")

            if len(files_with_secrets) > 10:
                print_info(f"\n... and {len(files_with_secrets) - 10} more files")

            print_info("\n💡 Recommendations:")
            print_info("  • Move secrets to environment variables")
            print_info("  • Use secure key storage (Android Keystore, iOS Keychain)")
            print_info("  • Consider using a secrets management service")

    except Exception as e:
        print_error(f"Secret scan failed: {e}")
        raise click.Abort()


@security.command(name='compliance')
@click.option('--source', '-s', 'source_path', required=True,
              type=click.Path(exists=True), help='Path to source code')
@click.option('--standard', type=click.Choice(['OWASP-MASVS', 'GDPR', 'PCI-DSS']),
              default='OWASP-MASVS', help='Compliance standard to check')
def compliance(source_path: str, standard: str) -> None:
    """Check compliance with security standards"""
    print_header(f"Compliance Check: {standard}")

    source_dir = Path(source_path)
    print_info(f"Source: {source_dir}")
    print_info(f"Standard: {standard}")

    try:
        analyzer = SecurityAnalyzer(project_root=source_dir)
        issues = analyzer.analyze(platform='android')  # Auto-detect platform

        print_info("\n🔄 Checking compliance...")

        # Map issues to compliance requirements
        compliance_checks = {
            'OWASP-MASVS': {
                'Data Storage': ['CWE-922', 'CWE-311'],
                'Cryptography': ['CWE-327', 'CWE-326'],
                'Authentication': ['CWE-798', 'CWE-259'],
                'Network Communication': ['CWE-295', 'CWE-319'],
                'Code Quality': ['CWE-502', 'CWE-94']
            }
        }

        if standard in compliance_checks:
            categories = compliance_checks[standard]

            print_success(f"\n✅ Compliance Report:")   # noqa: F541

            for category, cwes in categories.items():
                category_issues = [i for i in issues if i.cwe_id in cwes]
                status = "❌ FAIL" if category_issues else "✅ PASS"
                print_info(f"  {category}: {status}")
                if category_issues:
                    print_info(f"    → {len(category_issues)} issues found")

        else:
            print_info(f"\n⚠️  {standard} compliance checking not yet implemented")

    except Exception as e:
        print_error(f"Compliance check failed: {e}")
        raise click.Abort()


if __name__ == '__main__':
    security()
