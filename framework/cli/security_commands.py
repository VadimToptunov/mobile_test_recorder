"""
Security Scanning CLI Commands

Commands for automated security testing.

STEP 9: Advanced Security Testing CLI
"""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from framework.security.scanner import (
    SecurityScanner,
    SeverityLevel,
    SecurityScanResult,
)
from framework.security.advanced_security import (
    AdvancedSecurityScanner,
    HardcodedSecretsScanner,
    CertificatePinningAnalyzer,
    BinarySecurityAnalyzer,
    PrivacyComplianceChecker,
    RootJailbreakAnalyzer,
    SecureCodingAnalyzer,
    RiskLevel,
    OWASPMobileTop10,
)
from framework.security.sast_analyzer import SASTAnalyzer, VulnerabilityType
from framework.security.dast_analyzer import DASTAnalyzer
from framework.security.decompiler import Decompiler
from framework.security.supply_chain import SupplyChainAnalyzer
from framework.security.runtime_protection import RuntimeProtectionAnalyzer

console = Console()


@click.group()
def security() -> None:
    """
    Security scanning commands.

    Automated security testing following OWASP Mobile guidelines.
    """
    pass


@security.command()
@click.argument("app_path", type=Path)
@click.option("--platform", "-p", type=click.Choice(["android", "ios"]), required=True, help="Platform")
@click.option("--app-name", "-n", required=True, help="Application name")
@click.option("--app-version", "-v", default="1.0", help="Application version")
@click.option("--output", "-o", type=Path, help="Output report path")
@click.option("--format", "-f", type=click.Choice(["json", "html"]), default="json", help="Report format")
def scan(
        app_path: Path,
        platform: str,
        app_name: str,
        app_version: str,
        output: Optional[Path],
        format: str,
) -> None:
    """
    Scan mobile application for security vulnerabilities.

    APP_PATH: Path to APK or IPA file

    Example:
        observe security scan app.apk --platform android --app-name MyApp
        observe security scan app.ipa --platform ios --app-name MyApp -o report.json
    """
    if not app_path.exists():
        console.print(f"[red]✗[/red] File not found: {app_path}")
        raise SystemExit(1)

    console.print(f"[cyan]→[/cyan] Scanning {app_path}...\n")

    scanner = SecurityScanner()

    if platform == "android":
        result = scanner.scan_android(app_path, app_name, app_version)
    else:
        result = scanner.scan_ios(app_path, app_name, app_version)

    # Print summary
    _print_summary(result)

    # Generate report if requested
    if output:
        scanner.generate_report(result, output, format)
        console.print(f"\n[green]✓[/green] Report saved to {output}")

    # Exit code based on findings
    if result.critical_count > 0:
        raise SystemExit(2)
    elif result.high_count > 0:
        raise SystemExit(1)
    else:
        raise SystemExit(0)


@security.command()
@click.argument("app_path", type=Path)
@click.option("--platform", "-p", type=click.Choice(["android", "ios"]), required=True, help="Platform")
@click.option("--app-name", "-n", required=True, help="Application name")
@click.option("--app-version", "-v", default="1.0", help="Application version")
@click.option("--severity", "-s", type=click.Choice(["critical", "high", "medium", "low"]), help="Filter by severity")
def audit(
        app_path: Path,
        platform: str,
        app_name: str,
        app_version: str,
        severity: Optional[str],
) -> None:
    """
    Quick security audit with detailed findings.

    Example:
        observe security audit app.apk -p android -n MyApp
        observe security audit app.apk -p android -n MyApp --severity high
    """
    if not app_path.exists():
        console.print(f"[red]✗[/red] File not found: {app_path}")
        raise SystemExit(1)

    scanner = SecurityScanner()

    if platform == "android":
        result = scanner.scan_android(app_path, app_name, app_version)
    else:
        result = scanner.scan_ios(app_path, app_name, app_version)

    # Filter by severity if requested
    findings = result.findings
    if severity:
        severity_enum = {
            "critical": SeverityLevel.CRITICAL,
            "high": SeverityLevel.HIGH,
            "medium": SeverityLevel.MEDIUM,
            "low": SeverityLevel.LOW,
        }[severity]
        findings = [f for f in findings if f.severity == severity_enum]

    # Print detailed findings
    for finding in findings:
        severity_style = {
            SeverityLevel.CRITICAL: "red",
            SeverityLevel.HIGH: "yellow",
            SeverityLevel.MEDIUM: "blue",
            SeverityLevel.LOW: "dim",
        }[finding.severity]

        panel = Panel(
            f"[bold]{finding.description}[/bold]\n\n"
            f"[dim]Category:[/dim] {finding.category.value}\n"
            f"[dim]Location:[/dim] {finding.location}\n\n"
            f"[cyan]Recommendation:[/cyan]\n{finding.recommendation}",
            title=f"[{severity_style}]{finding.severity.value.upper()}[/{severity_style}] {finding.title}",
            border_style=severity_style,
        )
        console.print(panel)
        console.print()


@security.command(name="list")
def list_checks() -> None:
    """
    List available security checks.

    Example:
        observe security list
    """
    table = Table(title="OWASP Mobile Security Checks")
    table.add_column("Category", style="cyan")
    table.add_column("Description", style="dim")

    checks = [
        ("M1: Improper Platform Usage", "Misuse of platform features or security controls"),
        ("M2: Insecure Data Storage", "Sensitive data stored insecurely"),
        ("M3: Insecure Communication", "Unencrypted or weak network communication"),
        ("M4: Insecure Authentication", "Weak authentication mechanisms"),
        ("M5: Insufficient Cryptography", "Weak or broken cryptography"),
        ("M6: Insecure Authorization", "Poor authorization checks"),
        ("M7: Client Code Quality", "Code-level vulnerabilities"),
        ("M8: Code Tampering", "Binary patching, hooking, modification"),
        ("M9: Reverse Engineering", "Analysis of app binaries"),
        ("M10: Extraneous Functionality", "Hidden backdoors or debug code"),
    ]

    for category, description in checks:
        table.add_row(category, description)

    console.print(table)


@security.command()
@click.argument("app_name")
@click.argument("v1_report", type=Path)
@click.argument("v2_report", type=Path)
def compare(app_name: str, v1_report: Path, v2_report: Path) -> None:
    """
    Compare security reports between versions.

    Example:
        observe security compare MyApp v1_report.json v2_report.json
    """
    import json

    if not v1_report.exists() or not v2_report.exists():
        console.print("[red]✗[/red] Report file(s) not found")
        raise SystemExit(1)

    with open(v1_report, "r") as f:
        v1_data = json.load(f)

    with open(v2_report, "r") as f:
        v2_data = json.load(f)

    v1_summary = v1_data["summary"]
    v2_summary = v2_data["summary"]

    console.print(f"[bold cyan]Security Comparison: {app_name}[/bold cyan]\n")

    table = Table()
    table.add_column("Severity", style="cyan")
    table.add_column("Version 1", justify="right")
    table.add_column("Version 2", justify="right")
    table.add_column("Change", justify="right")

    for severity in ["critical", "high", "medium", "low"]:
        v1_count = v1_summary[severity]
        v2_count = v2_summary[severity]
        change = v2_count - v1_count

        change_str = ""
        if change > 0:
            change_str = f"[red]+{change}[/red]"
        elif change < 0:
            change_str = f"[green]{change}[/green]"
        else:
            change_str = "[dim]0[/dim]"

        table.add_row(
            severity.title(),
            str(v1_count),
            str(v2_count),
            change_str,
        )

    console.print(table)

    # Overall verdict
    total_v1 = v1_summary["total_findings"]
    total_v2 = v2_summary["total_findings"]

    if total_v2 < total_v1:
        console.print("\n[green]✓[/green] Security improved!")
    elif total_v2 > total_v1:
        console.print("\n[red]✗[/red] Security degraded!")
    else:
        console.print("\n[dim]No change in security posture[/dim]")


def _print_summary(result: SecurityScanResult) -> None:
    """Print security scan summary"""
    console.print(f"[bold]Security Scan Results: {result.app_name}[/bold]")
    console.print(f"Platform: {result.platform} | Version: {result.app_version}\n")

    table = Table()
    table.add_column("Severity", style="cyan")
    table.add_column("Count", justify="right", style="bold")

    severity_counts = [
        ("Critical", result.critical_count, "red"),
        ("High", result.high_count, "yellow"),
        ("Medium", result.medium_count, "blue"),
        ("Low", result.low_count, "dim"),
    ]

    for severity, count, style in severity_counts:
        if count > 0:
            table.add_row(severity, f"[{style}]{count}[/{style}]")
        else:
            table.add_row(severity, "[dim]0[/dim]")

    console.print(table)

    # Overall risk level
    if result.critical_count > 0:
        risk = "[red bold]CRITICAL RISK[/red bold]"
    elif result.high_count > 0:
        risk = "[yellow bold]HIGH RISK[/yellow bold]"
    elif result.medium_count > 0:
        risk = "[blue]MEDIUM RISK[/blue]"
    else:
        risk = "[green]LOW RISK[/green]"

    console.print(f"\nRisk Level: {risk}")


@security.command()
@click.argument("source_path", type=Path)
@click.option("--output", "-o", type=Path, help="Output report path")
@click.option("--format", "-f", type=click.Choice(["json", "sarif", "html"]), default="json", help="Report format")
def secrets(source_path: Path, output: Optional[Path], format: str) -> None:
    """
    Scan for hardcoded secrets in source code.

    Uses GitHub-level pattern detection with entropy analysis.

    Example:
        observe security secrets ./src
        observe security secrets ./project -o secrets_report.json
        observe security secrets ./app --format sarif
    """
    if not source_path.exists():
        console.print(f"[red]✗[/red] Path not found: {source_path}")
        raise SystemExit(1)

    console.print(Panel.fit("🔑 Hardcoded Secrets Scanner", style="bold red"))
    console.print(f"Scanning: {source_path}\n")

    scanner = HardcodedSecretsScanner()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning for secrets...", total=None)
        findings = scanner.scan_directory(source_path)
        progress.update(task, completed=True)

    if not findings:
        console.print("[green]✓[/green] No hardcoded secrets found!")
        raise SystemExit(0)

    # Display findings
    console.print(f"\n[red]⚠️ Found {len(findings)} potential secret(s)[/red]\n")

    for finding in findings[:20]:
        risk_style = {
            RiskLevel.CRITICAL: "red bold",
            RiskLevel.HIGH: "red",
            RiskLevel.MEDIUM: "yellow",
            RiskLevel.LOW: "dim",
            RiskLevel.INFO: "blue",
        }.get(finding.risk_level, "white")

        panel = Panel(
            f"[bold]{finding.title}[/bold]\n\n"
            f"[dim]File:[/dim] {finding.file_path}:{finding.line_number}\n"
            f"[dim]Secret Type:[/dim] {finding.metadata.get('secret_type', 'Unknown')}\n"
            f"[dim]Entropy:[/dim] {finding.metadata.get('entropy', 0):.2f}\n\n"
            f"[cyan]Evidence:[/cyan] {finding.evidence[:100]}...\n\n"
            f"[yellow]Recommendation:[/yellow] {finding.recommendation}",
            title=f"[{risk_style}]{finding.risk_level.value.upper()}[/{risk_style}]",
            border_style=risk_style.split()[0],
        )
        console.print(panel)
        console.print()

    if len(findings) > 20:
        console.print(f"[dim]... and {len(findings) - 20} more findings[/dim]")

    # Save report
    if output:
        if format == "sarif":
            scanner.export_sarif(findings, output)
        else:
            import json
            data = [f.to_dict() for f in findings]
            with open(output, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        console.print(f"\n[green]✓[/green] Report saved to {output}")

    raise SystemExit(1 if findings else 0)


@security.command()
@click.argument("app_path", type=Path)
@click.option("--platform", "-p", type=click.Choice(["android", "ios"]), required=True)
def pinning(app_path: Path, platform: str) -> None:
    """
    Analyze certificate pinning implementation.

    Checks for proper SSL/TLS pinning configuration.

    Example:
        observe security pinning app.apk --platform android
        observe security pinning app.ipa --platform ios
    """
    if not app_path.exists():
        console.print(f"[red]✗[/red] File not found: {app_path}")
        raise SystemExit(1)

    console.print(Panel.fit("🔐 Certificate Pinning Analysis", style="bold cyan"))

    analyzer = CertificatePinningAnalyzer()

    with console.status("[cyan]Analyzing certificate pinning..."):
        findings = analyzer.analyze(app_path, platform)

    if not findings:
        console.print("[green]✓[/green] Certificate pinning properly configured!")
        raise SystemExit(0)

    console.print(f"\n[yellow]⚠️ Found {len(findings)} pinning issue(s)[/yellow]\n")

    for finding in findings:
        console.print(f"[red]•[/red] {finding.title}")
        console.print(f"  {finding.description}")
        console.print(f"  [dim]Recommendation:[/dim] {finding.recommendation}")
        console.print()

    raise SystemExit(1)


@security.command()
@click.argument("binary_path", type=Path)
@click.option("--platform", "-p", type=click.Choice(["android", "ios"]), required=True)
def binary(binary_path: Path, platform: str) -> None:
    """
    Analyze binary security features.

    Checks for PIE, stack canaries, debuggable flags, etc.

    Example:
        observe security binary app.apk --platform android
        observe security binary app.ipa --platform ios
    """
    if not binary_path.exists():
        console.print(f"[red]✗[/red] File not found: {binary_path}")
        raise SystemExit(1)

    console.print(Panel.fit("🔬 Binary Security Analysis", style="bold magenta"))

    analyzer = BinarySecurityAnalyzer()

    with console.status("[cyan]Analyzing binary security..."):
        findings = analyzer.analyze(binary_path, platform)

    if not findings:
        console.print("[green]✓[/green] Binary security checks passed!")
        raise SystemExit(0)

    # Group by risk level
    critical = [f for f in findings if f.risk_level == RiskLevel.CRITICAL]
    high = [f for f in findings if f.risk_level == RiskLevel.HIGH]
    medium = [f for f in findings if f.risk_level == RiskLevel.MEDIUM]
    low = [f for f in findings if f.risk_level == RiskLevel.LOW]

    console.print()
    table = Table(title="Binary Security Findings")
    table.add_column("Risk", style="bold", width=10)
    table.add_column("Finding", style="white")
    table.add_column("Recommendation", style="cyan")

    for finding in critical:
        table.add_row("[red]CRITICAL[/red]", finding.title, finding.recommendation[:50])
    for finding in high:
        table.add_row("[yellow]HIGH[/yellow]", finding.title, finding.recommendation[:50])
    for finding in medium:
        table.add_row("[blue]MEDIUM[/blue]", finding.title, finding.recommendation[:50])
    for finding in low:
        table.add_row("[dim]LOW[/dim]", finding.title, finding.recommendation[:50])

    console.print(table)

    if critical:
        raise SystemExit(2)
    elif high:
        raise SystemExit(1)
    raise SystemExit(0)


@security.command()
@click.argument("source_path", type=Path)
@click.option("--regulation", "-r", type=click.Choice(["gdpr", "ccpa", "all"]), default="all")
@click.option("--output", "-o", type=Path, help="Output report path")
def privacy(source_path: Path, regulation: str, output: Optional[Path]) -> None:
    """
    Check privacy compliance (GDPR, CCPA).

    Analyzes code for privacy-related issues.

    Example:
        observe security privacy ./src --regulation gdpr
        observe security privacy ./app -r all -o privacy_report.json
    """
    if not source_path.exists():
        console.print(f"[red]✗[/red] Path not found: {source_path}")
        raise SystemExit(1)

    console.print(Panel.fit("🔒 Privacy Compliance Check", style="bold blue"))
    console.print(f"Regulation: {regulation.upper()}\n")

    checker = PrivacyComplianceChecker()

    with console.status("[cyan]Analyzing privacy compliance..."):
        findings = checker.check_compliance(source_path, regulation)

    if not findings:
        console.print(f"[green]✓[/green] No {regulation.upper()} compliance issues found!")
        raise SystemExit(0)

    console.print(f"\n[yellow]⚠️ Found {len(findings)} privacy issue(s)[/yellow]\n")

    for finding in findings:
        risk_style = "red" if finding.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH] else "yellow"

        console.print(f"[{risk_style}]•[/{risk_style}] [{risk_style}]{finding.title}[/{risk_style}]")
        console.print(f"  [dim]File:[/dim] {finding.file_path}:{finding.line_number}")
        console.print(f"  {finding.description}")
        console.print(f"  [cyan]Recommendation:[/cyan] {finding.recommendation}")
        console.print()

    if output:
        import json
        data = [f.to_dict() for f in findings]
        with open(output, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        console.print(f"\n[green]✓[/green] Report saved to {output}")

    raise SystemExit(1)


@security.command()
@click.argument("source_path", type=Path)
@click.option("--platform", "-p", type=click.Choice(["android", "ios", "all"]), default="all")
def rootcheck(source_path: Path, platform: str) -> None:
    """
    Analyze root/jailbreak detection implementation.

    Checks for proper detection mechanisms.

    Example:
        observe security rootcheck ./src --platform android
        observe security rootcheck ./app -p ios
    """
    if not source_path.exists():
        console.print(f"[red]✗[/red] Path not found: {source_path}")
        raise SystemExit(1)

    console.print(Panel.fit("📱 Root/Jailbreak Detection Analysis", style="bold yellow"))

    analyzer = RootJailbreakAnalyzer()

    with console.status("[cyan]Analyzing detection mechanisms..."):
        findings = analyzer.analyze(source_path, platform)

    if not findings:
        console.print("[green]✓[/green] Robust root/jailbreak detection in place!")
        raise SystemExit(0)

    console.print(f"\n[yellow]⚠️ Found {len(findings)} detection gap(s)[/yellow]\n")

    for finding in findings:
        console.print(f"[yellow]•[/yellow] {finding.title}")
        console.print(f"  {finding.description}")
        console.print(f"  [cyan]Recommendation:[/cyan] {finding.recommendation}")
        console.print()

    raise SystemExit(1)


@security.command()
@click.argument("source_path", type=Path)
@click.option("--language", "-l", type=click.Choice(["python", "kotlin", "swift", "java", "all"]), default="all")
@click.option("--output", "-o", type=Path, help="Output report path")
def code(source_path: Path, language: str, output: Optional[Path]) -> None:
    """
    Analyze secure coding practices.

    Checks for common vulnerabilities like SQL injection, XSS, etc.

    Example:
        observe security code ./src --language python
        observe security code ./app -l all -o code_report.json
    """
    if not source_path.exists():
        console.print(f"[red]✗[/red] Path not found: {source_path}")
        raise SystemExit(1)

    console.print(Panel.fit("📝 Secure Coding Analysis", style="bold cyan"))
    console.print(f"Language: {language.upper()}\n")

    analyzer = SecureCodingAnalyzer()

    with console.status("[cyan]Analyzing code security..."):
        findings = analyzer.analyze(source_path, language)

    if not findings:
        console.print("[green]✓[/green] No secure coding issues found!")
        raise SystemExit(0)

    # Group by OWASP category
    by_category = {}
    for finding in findings:
        cat = finding.owasp_category.value if finding.owasp_category else "Other"
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(finding)

    console.print(f"\n[red]⚠️ Found {len(findings)} issue(s)[/red]\n")

    for category, cat_findings in by_category.items():
        console.print(f"\n[bold]{category}[/bold] ({len(cat_findings)} issues)")

        for finding in cat_findings[:5]:
            risk_style = "red" if finding.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH] else "yellow"
            console.print(f"  [{risk_style}]•[/{risk_style}] {finding.title}")
            console.print(f"    [dim]{finding.file_path}:{finding.line_number}[/dim]")

        if len(cat_findings) > 5:
            console.print(f"    [dim]... and {len(cat_findings) - 5} more[/dim]")

    if output:
        import json
        data = [f.to_dict() for f in findings]
        with open(output, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        console.print(f"\n[green]✓[/green] Report saved to {output}")

    critical_count = len([f for f in findings if f.risk_level == RiskLevel.CRITICAL])
    if critical_count > 0:
        raise SystemExit(2)
    raise SystemExit(1)


@security.command()
@click.argument("app_path", type=Path)
@click.option("--platform", "-p", type=click.Choice(["android", "ios"]), required=True)
@click.option("--app-name", "-n", required=True, help="Application name")
@click.option("--output", "-o", type=Path, help="Output directory for reports")
@click.option("--format", "-f", type=click.Choice(["json", "sarif", "html"]), default="json")
def full(
    app_path: Path,
    platform: str,
    app_name: str,
    output: Optional[Path],
    format: str,
) -> None:
    """
    Run comprehensive security analysis.

    Combines all security checks into one comprehensive scan.

    Example:
        observe security full app.apk -p android -n MyApp -o ./reports
        observe security full app.ipa -p ios -n MyApp --format html
    """
    if not app_path.exists():
        console.print(f"[red]✗[/red] File not found: {app_path}")
        raise SystemExit(1)

    console.print(Panel.fit(
        f"🛡️ Comprehensive Security Analysis\n\n"
        f"App: {app_name}\n"
        f"Platform: {platform.upper()}",
        style="bold red"
    ))

    scanner = AdvancedSecurityScanner()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running full security scan...", total=None)
        result = scanner.full_scan(app_path, platform, app_name)
        progress.update(task, completed=True)

    # Summary
    console.print()
    console.print(Panel.fit("📊 Security Scan Summary", style="bold green"))

    summary_table = Table()
    summary_table.add_column("Category", style="cyan")
    summary_table.add_column("Critical", style="red", justify="right")
    summary_table.add_column("High", style="yellow", justify="right")
    summary_table.add_column("Medium", style="blue", justify="right")
    summary_table.add_column("Low", style="dim", justify="right")

    categories = {}
    for finding in result.findings:
        cat = finding.owasp_category.value if finding.owasp_category else "Other"
        if cat not in categories:
            categories[cat] = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        if finding.risk_level == RiskLevel.CRITICAL:
            categories[cat]["critical"] += 1
        elif finding.risk_level == RiskLevel.HIGH:
            categories[cat]["high"] += 1
        elif finding.risk_level == RiskLevel.MEDIUM:
            categories[cat]["medium"] += 1
        elif finding.risk_level == RiskLevel.LOW:
            categories[cat]["low"] += 1

    for cat, counts in sorted(categories.items()):
        summary_table.add_row(
            cat[:30],
            str(counts["critical"]) if counts["critical"] else "-",
            str(counts["high"]) if counts["high"] else "-",
            str(counts["medium"]) if counts["medium"] else "-",
            str(counts["low"]) if counts["low"] else "-",
        )

    console.print(summary_table)

    # Overall stats
    total = len(result.findings)
    critical = len([f for f in result.findings if f.risk_level == RiskLevel.CRITICAL])
    high = len([f for f in result.findings if f.risk_level == RiskLevel.HIGH])

    console.print(f"\n[bold]Total Findings:[/bold] {total}")
    console.print(f"[red]Critical:[/red] {critical} | [yellow]High:[/yellow] {high}")

    # Risk level
    if critical > 0:
        console.print("\n[red bold]🚨 CRITICAL RISK - Immediate action required![/red bold]")
    elif high > 0:
        console.print("\n[yellow bold]⚠️ HIGH RISK - Action recommended[/yellow bold]")
    elif total > 0:
        console.print("\n[blue]ℹ️ MODERATE RISK - Review recommended[/blue]")
    else:
        console.print("\n[green]✓ LOW RISK - No significant issues found[/green]")

    # Save reports
    if output:
        output.mkdir(parents=True, exist_ok=True)

        if format == "sarif":
            sarif_path = output / f"{app_name}_security.sarif"
            scanner.export_sarif(result.findings, sarif_path)
            console.print(f"\n[green]✓[/green] SARIF report: {sarif_path}")
        elif format == "html":
            html_path = output / f"{app_name}_security.html"
            scanner.export_html(result, html_path)
            console.print(f"\n[green]✓[/green] HTML report: {html_path}")
        else:
            import json
            json_path = output / f"{app_name}_security.json"
            with open(json_path, 'w') as f:
                json.dump(result.to_dict(), f, indent=2, default=str)
            console.print(f"\n[green]✓[/green] JSON report: {json_path}")

    if critical > 0:
        raise SystemExit(2)
    elif high > 0:
        raise SystemExit(1)
    raise SystemExit(0)


@security.command()
def owasp() -> None:
    """
    Display OWASP Mobile Top 10 2024 categories.

    Example:
        observe security owasp
    """
    console.print(Panel.fit("📋 OWASP Mobile Top 10 (2024)", style="bold cyan"))

    table = Table()
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Category", style="bold")
    table.add_column("Description", style="white")

    owasp_items = [
        ("M1", "Improper Credential Usage", "Hardcoded credentials, insecure storage of secrets"),
        ("M2", "Inadequate Supply Chain Security", "Third-party dependencies, SDK vulnerabilities"),
        ("M3", "Insecure Authentication/Authorization", "Weak auth, broken access control"),
        ("M4", "Insufficient Input/Output Validation", "Injection attacks, XSS, path traversal"),
        ("M5", "Insecure Communication", "Cleartext traffic, weak TLS, missing cert pinning"),
        ("M6", "Inadequate Privacy Controls", "PII exposure, tracking, data minimization"),
        ("M7", "Insufficient Binary Protections", "Missing obfuscation, debuggable, no tamper detection"),
        ("M8", "Security Misconfiguration", "Debug enabled, weak permissions, exposed components"),
        ("M9", "Insecure Data Storage", "Unencrypted databases, logs with sensitive data"),
        ("M10", "Insufficient Cryptography", "Weak algorithms, hardcoded keys, improper implementation"),
    ]

    for id_, name, desc in owasp_items:
        table.add_row(id_, name, desc)

    console.print(table)

    console.print("\n[dim]Run 'observe security full' for comprehensive OWASP coverage[/dim]")


# =============================================================================
# SAST (Static Application Security Testing) Commands
# =============================================================================


@security.command()
@click.argument("source_path", type=Path)
@click.option("--language", "-l", type=click.Choice(["python", "java", "kotlin", "swift", "javascript", "all"]), default="all")
@click.option("--output", "-o", type=Path, help="Output report path")
@click.option("--format", "-f", type=click.Choice(["json", "sarif", "html"]), default="json")
@click.option("--taint/--no-taint", default=True, help="Enable taint analysis")
@click.option("--crypto/--no-crypto", default=True, help="Enable cryptography analysis")
def sast(
    source_path: Path,
    language: str,
    output: Optional[Path],
    format: str,
    taint: bool,
    crypto: bool,
) -> None:
    """
    Run Static Application Security Testing (SAST).

    Comprehensive static analysis with taint tracking, control flow analysis,
    and cryptography vulnerability detection.

    Example:
        observe security sast ./src --language python
        observe security sast ./app -l java -o sast_report.sarif --format sarif
        observe security sast ./project --taint --crypto
    """
    if not source_path.exists():
        console.print(f"[red]✗[/red] Path not found: {source_path}")
        raise SystemExit(1)

    console.print(Panel.fit(
        "🔍 Static Application Security Testing (SAST)\n\n"
        f"Source: {source_path}\n"
        f"Language: {language.upper()}\n"
        f"Taint Analysis: {'Enabled' if taint else 'Disabled'}\n"
        f"Crypto Analysis: {'Enabled' if crypto else 'Disabled'}",
        style="bold cyan"
    ))

    analyzer = SASTAnalyzer()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running SAST analysis...", total=None)
        result = analyzer.analyze(
            source_path,
            language=language if language != "all" else None,
            enable_taint=taint,
            enable_crypto=crypto,
        )
        progress.update(task, completed=True)

    # Summary by vulnerability type
    console.print()
    console.print(Panel.fit("📊 SAST Analysis Results", style="bold green"))

    if not result.vulnerabilities:
        console.print("[green]✓[/green] No vulnerabilities found!")
        raise SystemExit(0)

    # Group by type
    by_type: dict = {}
    for vuln in result.vulnerabilities:
        vtype = vuln.vulnerability_type.value
        if vtype not in by_type:
            by_type[vtype] = []
        by_type[vtype].append(vuln)

    table = Table(title=f"Found {len(result.vulnerabilities)} Vulnerabilities")
    table.add_column("Type", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Critical", style="red", justify="right")
    table.add_column("High", style="yellow", justify="right")

    for vtype, vulns in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
        critical = len([v for v in vulns if v.severity == "critical"])
        high = len([v for v in vulns if v.severity == "high"])
        table.add_row(vtype, str(len(vulns)), str(critical) if critical else "-", str(high) if high else "-")

    console.print(table)

    # Show top findings
    console.print("\n[bold]Top Findings:[/bold]")
    critical_vulns = [v for v in result.vulnerabilities if v.severity == "critical"]
    high_vulns = [v for v in result.vulnerabilities if v.severity == "high"]

    for vuln in (critical_vulns + high_vulns)[:10]:
        severity_style = "red bold" if vuln.severity == "critical" else "yellow"
        console.print(f"  [{severity_style}]•[/{severity_style}] [{severity_style}]{vuln.vulnerability_type.value}[/{severity_style}]")
        console.print(f"    [dim]File:[/dim] {vuln.file_path}:{vuln.line_number}")
        console.print(f"    [dim]CWE:[/dim] {vuln.cwe_id} | {vuln.description[:60]}...")
        if vuln.taint_flow:
            console.print(f"    [dim]Taint Flow:[/dim] {vuln.taint_flow.source} → {vuln.taint_flow.sink}")
        console.print()

    # Save report
    if output:
        if format == "sarif":
            analyzer.export_sarif(result, output)
        elif format == "html":
            analyzer.export_html(result, output)
        else:
            import json
            with open(output, 'w') as f:
                json.dump(result.to_dict(), f, indent=2, default=str)
        console.print(f"\n[green]✓[/green] Report saved to {output}")

    if critical_vulns:
        raise SystemExit(2)
    elif high_vulns:
        raise SystemExit(1)
    raise SystemExit(0)


@security.command()
@click.argument("source_path", type=Path)
@click.option("--output", "-o", type=Path, help="Output report path")
def taint(source_path: Path, output: Optional[Path]) -> None:
    """
    Run taint analysis to track data flow from sources to sinks.

    Identifies injection vulnerabilities by tracing untrusted input.

    Example:
        observe security taint ./src
        observe security taint ./app -o taint_report.json
    """
    if not source_path.exists():
        console.print(f"[red]✗[/red] Path not found: {source_path}")
        raise SystemExit(1)

    console.print(Panel.fit("🔬 Taint Flow Analysis", style="bold magenta"))

    analyzer = SASTAnalyzer()

    with console.status("[cyan]Analyzing taint flows..."):
        result = analyzer.analyze(source_path, enable_taint=True, enable_crypto=False)

    taint_vulns = [v for v in result.vulnerabilities if v.taint_flow]

    if not taint_vulns:
        console.print("[green]✓[/green] No taint flow vulnerabilities found!")
        raise SystemExit(0)

    console.print(f"\n[red]⚠️ Found {len(taint_vulns)} taint flow issue(s)[/red]\n")

    for vuln in taint_vulns[:15]:
        flow = vuln.taint_flow
        severity_style = "red" if vuln.severity in ["critical", "high"] else "yellow"

        panel = Panel(
            f"[bold]{vuln.vulnerability_type.value}[/bold]\n\n"
            f"[dim]Source:[/dim] {flow.source} (line {flow.source_line})\n"
            f"[dim]Sink:[/dim] {flow.sink} (line {flow.sink_line})\n"
            f"[dim]File:[/dim] {vuln.file_path}\n"
            f"[dim]Path Length:[/dim] {len(flow.path)} nodes\n\n"
            f"[cyan]Flow Path:[/cyan]\n" + " → ".join(flow.path[:5]) +
            (f" → ... ({len(flow.path) - 5} more)" if len(flow.path) > 5 else "") +
            f"\n\n[yellow]CWE-{vuln.cwe_id}:[/yellow] {vuln.description}",
            title=f"[{severity_style}]{vuln.severity.upper()}[/{severity_style}]",
            border_style=severity_style,
        )
        console.print(panel)
        console.print()

    if output:
        import json
        data = [v.to_dict() for v in taint_vulns]
        with open(output, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        console.print(f"\n[green]✓[/green] Report saved to {output}")

    raise SystemExit(1)


# =============================================================================
# DAST (Dynamic Application Security Testing) Commands
# =============================================================================


@security.command()
@click.argument("target", type=str)
@click.option("--port", "-p", type=int, default=443, help="Target port")
@click.option("--output", "-o", type=Path, help="Output report path")
@click.option("--format", "-f", type=click.Choice(["json", "html"]), default="json")
def dast(target: str, port: int, output: Optional[Path], format: str) -> None:
    """
    Run Dynamic Application Security Testing (DAST).

    Tests running application for SSL/TLS, API security, and session vulnerabilities.

    Example:
        observe security dast api.example.com
        observe security dast 192.168.1.100 --port 8443 -o dast_report.json
    """
    console.print(Panel.fit(
        "⚡ Dynamic Application Security Testing (DAST)\n\n"
        f"Target: {target}:{port}\n"
        f"Tests: SSL/TLS, API Security, Session Analysis",
        style="bold yellow"
    ))

    analyzer = DASTAnalyzer()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running DAST analysis...", total=None)
        result = analyzer.analyze(target, port)
        progress.update(task, completed=True)

    console.print()
    console.print(Panel.fit("📊 DAST Analysis Results", style="bold green"))

    if not result.findings:
        console.print("[green]✓[/green] No vulnerabilities found!")
        raise SystemExit(0)

    # Summary table
    table = Table(title=f"Found {len(result.findings)} Issues")
    table.add_column("Category", style="cyan")
    table.add_column("Severity", style="bold")
    table.add_column("Finding")

    for finding in result.findings:
        severity_style = {
            "critical": "red bold",
            "high": "red",
            "medium": "yellow",
            "low": "dim",
        }.get(finding.severity, "white")

        table.add_row(
            finding.category,
            f"[{severity_style}]{finding.severity.upper()}[/{severity_style}]",
            finding.title[:50] + ("..." if len(finding.title) > 50 else ""),
        )

    console.print(table)

    # Detailed findings
    console.print("\n[bold]Detailed Findings:[/bold]\n")

    for finding in result.findings[:10]:
        severity_style = "red" if finding.severity in ["critical", "high"] else "yellow"
        console.print(f"[{severity_style}]•[/{severity_style}] [{severity_style}]{finding.title}[/{severity_style}]")
        console.print(f"  [dim]Category:[/dim] {finding.category}")
        console.print(f"  {finding.description}")
        console.print(f"  [cyan]Recommendation:[/cyan] {finding.recommendation}")
        console.print()

    if output:
        if format == "html":
            analyzer.export_html(result, output)
        else:
            import json
            with open(output, 'w') as f:
                json.dump(result.to_dict(), f, indent=2, default=str)
        console.print(f"\n[green]✓[/green] Report saved to {output}")

    critical = len([f for f in result.findings if f.severity == "critical"])
    if critical:
        raise SystemExit(2)
    raise SystemExit(1)


@security.command()
@click.argument("host", type=str)
@click.option("--port", "-p", type=int, default=443, help="Target port")
def ssl(host: str, port: int) -> None:
    """
    Analyze SSL/TLS configuration.

    Checks for weak protocols, cipher suites, and certificate issues.

    Example:
        observe security ssl api.example.com
        observe security ssl 192.168.1.100 --port 8443
    """
    console.print(Panel.fit(f"🔐 SSL/TLS Analysis: {host}:{port}", style="bold cyan"))

    analyzer = DASTAnalyzer()

    with console.status("[cyan]Analyzing SSL/TLS configuration..."):
        result = analyzer.analyze_ssl(host, port)

    if not result.findings:
        console.print("[green]✓[/green] SSL/TLS configuration is secure!")
        console.print(f"\n[dim]Protocol: {result.protocol}[/dim]")
        console.print(f"[dim]Cipher: {result.cipher_suite}[/dim]")
        console.print(f"[dim]Certificate Valid Until: {result.cert_expiry}[/dim]")
        raise SystemExit(0)

    console.print(f"\n[yellow]⚠️ Found {len(result.findings)} SSL/TLS issue(s)[/yellow]\n")

    table = Table()
    table.add_column("Severity", style="bold", width=10)
    table.add_column("Issue", style="white")
    table.add_column("Recommendation", style="cyan")

    for finding in result.findings:
        severity_style = {
            "critical": "red",
            "high": "yellow",
            "medium": "blue",
            "low": "dim",
        }.get(finding.severity, "white")

        table.add_row(
            f"[{severity_style}]{finding.severity.upper()}[/{severity_style}]",
            finding.title,
            finding.recommendation[:40] + "...",
        )

    console.print(table)

    raise SystemExit(1)


@security.command()
@click.argument("base_url", type=str)
@click.option("--auth-header", "-a", type=str, help="Authorization header value")
@click.option("--endpoints", "-e", type=Path, help="File with endpoint definitions")
def api(base_url: str, auth_header: Optional[str], endpoints: Optional[Path]) -> None:
    """
    Test API security vulnerabilities.

    Checks for injection, authentication bypass, and IDOR vulnerabilities.

    Example:
        observe security api https://api.example.com
        observe security api https://api.example.com -a "Bearer token123"
        observe security api https://api.example.com -e endpoints.json
    """
    console.print(Panel.fit(f"🌐 API Security Testing: {base_url}", style="bold green"))

    analyzer = DASTAnalyzer()

    headers = {}
    if auth_header:
        headers["Authorization"] = auth_header

    endpoint_list = None
    if endpoints and endpoints.exists():
        import json
        with open(endpoints) as f:
            endpoint_list = json.load(f)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Testing API endpoints...", total=None)
        result = analyzer.test_api(base_url, headers, endpoint_list)
        progress.update(task, completed=True)

    if not result.findings:
        console.print("[green]✓[/green] No API security issues found!")
        raise SystemExit(0)

    console.print(f"\n[red]⚠️ Found {len(result.findings)} API vulnerability(ies)[/red]\n")

    for finding in result.findings:
        severity_style = "red" if finding.severity in ["critical", "high"] else "yellow"

        panel = Panel(
            f"[bold]{finding.title}[/bold]\n\n"
            f"[dim]Endpoint:[/dim] {finding.endpoint}\n"
            f"[dim]Method:[/dim] {finding.method}\n"
            f"[dim]Vulnerability:[/dim] {finding.vulnerability_type}\n\n"
            f"{finding.description}\n\n"
            f"[cyan]Recommendation:[/cyan] {finding.recommendation}",
            title=f"[{severity_style}]{finding.severity.upper()}[/{severity_style}]",
            border_style=severity_style,
        )
        console.print(panel)
        console.print()

    raise SystemExit(1)


# =============================================================================
# Decompilation & Reverse Engineering Commands
# =============================================================================


@security.command()
@click.argument("binary_path", type=Path)
@click.option("--output", "-o", type=Path, help="Output directory for decompiled files")
@click.option("--extract-strings/--no-strings", default=True, help="Extract strings from binary")
@click.option("--analyze-native/--no-native", default=True, help="Analyze native libraries")
def decompile(
    binary_path: Path,
    output: Optional[Path],
    extract_strings: bool,
    analyze_native: bool,
) -> None:
    """
    Decompile and analyze mobile application binary.

    Supports APK (Android) and IPA (iOS) files.

    Example:
        observe security decompile app.apk
        observe security decompile app.ipa -o ./decompiled
        observe security decompile app.apk --extract-strings --analyze-native
    """
    if not binary_path.exists():
        console.print(f"[red]✗[/red] File not found: {binary_path}")
        raise SystemExit(1)

    platform = "android" if binary_path.suffix.lower() == ".apk" else "ios"

    console.print(Panel.fit(
        f"🔧 Binary Decompilation & Analysis\n\n"
        f"File: {binary_path.name}\n"
        f"Platform: {platform.upper()}\n"
        f"String Extraction: {'Enabled' if extract_strings else 'Disabled'}\n"
        f"Native Analysis: {'Enabled' if analyze_native else 'Disabled'}",
        style="bold magenta"
    ))

    decompiler = Decompiler()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Decompiling binary...", total=None)
        result = decompiler.decompile(
            binary_path,
            output_dir=output,
            extract_strings=extract_strings,
            analyze_native=analyze_native,
        )
        progress.update(task, completed=True)

    console.print()
    console.print(Panel.fit("📊 Decompilation Results", style="bold green"))

    # Basic info
    info_table = Table(title="Binary Information")
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="white")

    info_table.add_row("Package", result.package_name)
    info_table.add_row("Version", result.version)
    info_table.add_row("Min SDK", str(result.min_sdk) if result.min_sdk else "N/A")
    info_table.add_row("Target SDK", str(result.target_sdk) if result.target_sdk else "N/A")
    info_table.add_row("SHA256", result.sha256[:32] + "...")
    info_table.add_row("Size", f"{result.size_bytes / 1024 / 1024:.2f} MB")

    console.print(info_table)

    # Protection analysis
    if result.protections:
        console.print("\n[bold]Protection Mechanisms Detected:[/bold]")

        protection_table = Table()
        protection_table.add_column("Protection", style="cyan")
        protection_table.add_column("Status", style="bold")
        protection_table.add_column("Details", style="dim")

        for prot in result.protections:
            status_style = "green" if prot.detected else "red"
            status = "Detected" if prot.detected else "Not Found"
            protection_table.add_row(
                prot.name,
                f"[{status_style}]{status}[/{status_style}]",
                prot.details[:40] if prot.details else "-",
            )

        console.print(protection_table)

    # Strings of interest
    if result.interesting_strings:
        console.print(f"\n[bold]Interesting Strings Found ({len(result.interesting_strings)}):[/bold]")

        for string_info in result.interesting_strings[:15]:
            category_style = {
                "url": "blue",
                "api_key": "red",
                "password": "red",
                "email": "yellow",
                "ip_address": "cyan",
                "secret": "red",
            }.get(string_info.category, "white")

            console.print(f"  [{category_style}]•[/{category_style}] [{category_style}]{string_info.category}[/{category_style}]: {string_info.value[:60]}...")

        if len(result.interesting_strings) > 15:
            console.print(f"  [dim]... and {len(result.interesting_strings) - 15} more[/dim]")

    # Native libraries
    if result.native_libs:
        console.print(f"\n[bold]Native Libraries ({len(result.native_libs)}):[/bold]")

        for lib in result.native_libs[:10]:
            arch_str = ", ".join(lib.architectures) if lib.architectures else "Unknown"
            console.print(f"  [cyan]•[/cyan] {lib.name} ({arch_str})")

    # Security findings
    if result.security_findings:
        console.print(f"\n[bold red]⚠️ Security Findings ({len(result.security_findings)}):[/bold red]")

        for finding in result.security_findings[:10]:
            severity_style = "red" if finding.severity in ["critical", "high"] else "yellow"
            console.print(f"  [{severity_style}]•[/{severity_style}] [{severity_style}]{finding.title}[/{severity_style}]")
            console.print(f"    {finding.description}")

    if output:
        console.print(f"\n[green]✓[/green] Decompiled files saved to {output}")

    raise SystemExit(0)


@security.command()
@click.argument("binary_path", type=Path)
@click.option("--output", "-o", type=Path, help="Output file for strings")
@click.option("--min-length", "-m", type=int, default=8, help="Minimum string length")
@click.option("--filter", "-f", type=click.Choice(["all", "urls", "secrets", "emails", "ips"]), default="all")
def strings(
    binary_path: Path,
    output: Optional[Path],
    min_length: int,
    filter: str,
) -> None:
    """
    Extract strings from binary.

    Extracts and categorizes interesting strings from APK/IPA files.

    Example:
        observe security strings app.apk
        observe security strings app.ipa -o strings.txt --filter secrets
        observe security strings app.apk --min-length 12
    """
    if not binary_path.exists():
        console.print(f"[red]✗[/red] File not found: {binary_path}")
        raise SystemExit(1)

    console.print(Panel.fit(f"📝 String Extraction: {binary_path.name}", style="bold cyan"))

    decompiler = Decompiler()

    with console.status("[cyan]Extracting strings..."):
        strings_list = decompiler.extract_strings(binary_path, min_length=min_length)

    if filter != "all":
        filter_map = {
            "urls": ["url", "endpoint"],
            "secrets": ["api_key", "password", "secret", "token"],
            "emails": ["email"],
            "ips": ["ip_address"],
        }
        categories = filter_map.get(filter, [])
        strings_list = [s for s in strings_list if s.category in categories]

    if not strings_list:
        console.print("[dim]No strings found matching criteria[/dim]")
        raise SystemExit(0)

    console.print(f"\n[bold]Found {len(strings_list)} strings[/bold]\n")

    # Group by category
    by_category: dict = {}
    for s in strings_list:
        if s.category not in by_category:
            by_category[s.category] = []
        by_category[s.category].append(s)

    for category, cat_strings in sorted(by_category.items()):
        category_style = {
            "url": "blue",
            "api_key": "red",
            "password": "red",
            "email": "yellow",
            "ip_address": "cyan",
            "secret": "red",
        }.get(category, "white")

        console.print(f"[{category_style}][bold]{category.upper()}[/bold][/{category_style}] ({len(cat_strings)})")

        for s in cat_strings[:10]:
            console.print(f"  {s.value[:80]}{'...' if len(s.value) > 80 else ''}")

        if len(cat_strings) > 10:
            console.print(f"  [dim]... and {len(cat_strings) - 10} more[/dim]")
        console.print()

    if output:
        with open(output, 'w') as f:
            for s in strings_list:
                f.write(f"[{s.category}] {s.value}\n")
        console.print(f"\n[green]✓[/green] Strings saved to {output}")

    raise SystemExit(0)


# =============================================================================
# Supply Chain Security Commands
# =============================================================================


@security.command(name="supply-chain")
@click.argument("project_path", type=Path)
@click.option("--output", "-o", type=Path, help="Output report path")
@click.option("--format", "-f", type=click.Choice(["json", "sbom", "html"]), default="json")
@click.option("--check-vulns/--no-vulns", default=True, help="Check for known vulnerabilities")
def supply_chain(
    project_path: Path,
    output: Optional[Path],
    format: str,
    check_vulns: bool,
) -> None:
    """
    Analyze supply chain security.

    Scans dependencies for vulnerabilities, generates SBOM, and checks licenses.

    Example:
        observe security supply-chain ./project
        observe security supply-chain ./app -o sbom.json --format sbom
        observe security supply-chain ./src --check-vulns
    """
    if not project_path.exists():
        console.print(f"[red]✗[/red] Path not found: {project_path}")
        raise SystemExit(1)

    console.print(Panel.fit(
        "📦 Supply Chain Security Analysis\n\n"
        f"Project: {project_path}\n"
        f"Vulnerability Check: {'Enabled' if check_vulns else 'Disabled'}",
        style="bold blue"
    ))

    analyzer = SupplyChainAnalyzer()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing dependencies...", total=None)
        result = analyzer.analyze(project_path, check_vulnerabilities=check_vulns)
        progress.update(task, completed=True)

    console.print()
    console.print(Panel.fit("📊 Supply Chain Analysis Results", style="bold green"))

    # Dependency summary
    dep_table = Table(title=f"Dependencies ({len(result.dependencies)})")
    dep_table.add_column("Ecosystem", style="cyan")
    dep_table.add_column("Count", justify="right")
    dep_table.add_column("Vulnerable", style="red", justify="right")

    by_ecosystem: dict = {}
    for dep in result.dependencies:
        eco = dep.ecosystem
        if eco not in by_ecosystem:
            by_ecosystem[eco] = {"total": 0, "vulnerable": 0}
        by_ecosystem[eco]["total"] += 1
        if dep.vulnerabilities:
            by_ecosystem[eco]["vulnerable"] += 1

    for eco, counts in by_ecosystem.items():
        dep_table.add_row(
            eco,
            str(counts["total"]),
            str(counts["vulnerable"]) if counts["vulnerable"] else "-",
        )

    console.print(dep_table)

    # Vulnerabilities
    if result.vulnerabilities:
        console.print(f"\n[bold red]⚠️ Vulnerable Dependencies ({len(result.vulnerabilities)}):[/bold red]\n")

        vuln_table = Table()
        vuln_table.add_column("Package", style="cyan")
        vuln_table.add_column("Version", style="dim")
        vuln_table.add_column("CVE", style="red")
        vuln_table.add_column("Severity", style="bold")
        vuln_table.add_column("Fixed In", style="green")

        for vuln in result.vulnerabilities[:20]:
            severity_style = {
                "critical": "red bold",
                "high": "red",
                "medium": "yellow",
                "low": "dim",
            }.get(vuln.severity, "white")

            vuln_table.add_row(
                vuln.package_name,
                vuln.installed_version,
                vuln.cve_id or "N/A",
                f"[{severity_style}]{vuln.severity.upper()}[/{severity_style}]",
                vuln.fixed_version or "Unknown",
            )

        console.print(vuln_table)

        if len(result.vulnerabilities) > 20:
            console.print(f"\n[dim]... and {len(result.vulnerabilities) - 20} more vulnerabilities[/dim]")

    # License issues
    if result.license_issues:
        console.print(f"\n[bold yellow]⚠️ License Issues ({len(result.license_issues)}):[/bold yellow]")

        for issue in result.license_issues[:10]:
            console.print(f"  [yellow]•[/yellow] {issue.package_name}: {issue.license} - {issue.issue}")

    # Save report
    if output:
        if format == "sbom":
            analyzer.generate_sbom(result, output)
            console.print(f"\n[green]✓[/green] SBOM saved to {output}")
        elif format == "html":
            analyzer.export_html(result, output)
            console.print(f"\n[green]✓[/green] HTML report saved to {output}")
        else:
            import json
            with open(output, 'w') as f:
                json.dump(result.to_dict(), f, indent=2, default=str)
            console.print(f"\n[green]✓[/green] Report saved to {output}")

    critical_vulns = len([v for v in result.vulnerabilities if v.severity == "critical"])
    if critical_vulns:
        raise SystemExit(2)
    elif result.vulnerabilities:
        raise SystemExit(1)
    raise SystemExit(0)


@security.command()
@click.argument("project_path", type=Path)
@click.option("--output", "-o", type=Path, required=True, help="Output SBOM file path")
@click.option("--format", "-f", type=click.Choice(["cyclonedx", "spdx"]), default="cyclonedx")
def sbom(project_path: Path, output: Path, format: str) -> None:
    """
    Generate Software Bill of Materials (SBOM).

    Creates a comprehensive inventory of all dependencies.

    Example:
        observe security sbom ./project -o sbom.json
        observe security sbom ./app -o sbom.xml --format spdx
    """
    if not project_path.exists():
        console.print(f"[red]✗[/red] Path not found: {project_path}")
        raise SystemExit(1)

    console.print(Panel.fit(f"📋 SBOM Generation ({format.upper()})", style="bold cyan"))

    analyzer = SupplyChainAnalyzer()

    with console.status("[cyan]Generating SBOM..."):
        result = analyzer.analyze(project_path, check_vulnerabilities=False)
        analyzer.generate_sbom(result, output, format=format)

    console.print(f"\n[green]✓[/green] SBOM generated: {output}")
    console.print(f"[dim]Format: {format.upper()}[/dim]")
    console.print(f"[dim]Components: {len(result.dependencies)}[/dim]")

    raise SystemExit(0)


# =============================================================================
# Runtime Protection Analysis Commands
# =============================================================================


@security.command(name="runtime")
@click.argument("app_path", type=Path)
@click.option("--platform", "-p", type=click.Choice(["android", "ios"]), required=True)
@click.option("--output", "-o", type=Path, help="Output report path")
@click.option("--format", "-f", type=click.Choice(["json", "html"]), default="json")
def runtime(
    app_path: Path,
    platform: str,
    output: Optional[Path],
    format: str,
) -> None:
    """
    Analyze runtime protection mechanisms.

    Checks for root/jailbreak detection, anti-debugging, anti-tampering, etc.

    Example:
        observe security runtime app.apk --platform android
        observe security runtime app.ipa -p ios -o runtime_report.json
    """
    if not app_path.exists():
        console.print(f"[red]✗[/red] File not found: {app_path}")
        raise SystemExit(1)

    console.print(Panel.fit(
        f"🛡️ Runtime Protection Analysis\n\n"
        f"App: {app_path.name}\n"
        f"Platform: {platform.upper()}",
        style="bold red"
    ))

    analyzer = RuntimeProtectionAnalyzer()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing runtime protections...", total=None)
        result = analyzer.analyze(app_path, platform)
        progress.update(task, completed=True)

    console.print()
    console.print(Panel.fit("📊 Runtime Protection Results", style="bold green"))

    # Protection matrix
    protection_table = Table(title="Protection Mechanisms")
    protection_table.add_column("Protection", style="cyan")
    protection_table.add_column("Status", style="bold", justify="center")
    protection_table.add_column("Strength", justify="center")
    protection_table.add_column("Details", style="dim")

    protections = [
        ("Root/Jailbreak Detection", result.root_detection),
        ("Emulator Detection", result.emulator_detection),
        ("Debug Detection", result.debug_detection),
        ("Tamper Detection", result.tamper_detection),
        ("Hook Detection (Frida/Xposed)", result.hook_detection),
        ("SSL Pinning", result.ssl_pinning),
        ("Code Obfuscation", result.obfuscation),
    ]

    for name, protection in protections:
        if protection.detected:
            status = "[green]✓ Detected[/green]"
            strength_color = {"strong": "green", "medium": "yellow", "weak": "red"}.get(protection.strength, "white")
            strength = f"[{strength_color}]{protection.strength.upper()}[/{strength_color}]"
        else:
            status = "[red]✗ Missing[/red]"
            strength = "[dim]-[/dim]"

        protection_table.add_row(
            name,
            status,
            strength,
            protection.details[:30] + "..." if protection.details and len(protection.details) > 30 else (protection.details or "-"),
        )

    console.print(protection_table)

    # Overall score
    detected_count = sum(1 for _, p in protections if p.detected)
    score = (detected_count / len(protections)) * 100

    if score >= 80:
        score_style = "green bold"
        verdict = "EXCELLENT"
    elif score >= 60:
        score_style = "yellow bold"
        verdict = "GOOD"
    elif score >= 40:
        score_style = "yellow"
        verdict = "MODERATE"
    else:
        score_style = "red bold"
        verdict = "WEAK"

    console.print(f"\n[bold]Protection Score:[/bold] [{score_style}]{score:.0f}% - {verdict}[/{score_style}]")

    # Recommendations
    if result.recommendations:
        console.print("\n[bold]Recommendations:[/bold]")
        for rec in result.recommendations[:5]:
            console.print(f"  [cyan]•[/cyan] {rec}")

    # Bypass methods found
    if result.bypass_methods:
        console.print(f"\n[bold red]⚠️ Potential Bypass Methods ({len(result.bypass_methods)}):[/bold red]")
        for bypass in result.bypass_methods[:5]:
            console.print(f"  [red]•[/red] {bypass.method}: {bypass.description}")

    if output:
        if format == "html":
            analyzer.export_html(result, output)
        else:
            import json
            with open(output, 'w') as f:
                json.dump(result.to_dict(), f, indent=2, default=str)
        console.print(f"\n[green]✓[/green] Report saved to {output}")

    if score < 40:
        raise SystemExit(1)
    raise SystemExit(0)


@security.command()
@click.argument("app_path", type=Path)
@click.option("--platform", "-p", type=click.Choice(["android", "ios"]), required=True)
def protections(app_path: Path, platform: str) -> None:
    """
    Quick check for runtime protections.

    Rapidly scans for common protection mechanisms.

    Example:
        observe security protections app.apk -p android
        observe security protections app.ipa -p ios
    """
    if not app_path.exists():
        console.print(f"[red]✗[/red] File not found: {app_path}")
        raise SystemExit(1)

    console.print(Panel.fit(f"🔒 Quick Protection Check: {app_path.name}", style="bold cyan"))

    analyzer = RuntimeProtectionAnalyzer()

    with console.status("[cyan]Checking protections..."):
        result = analyzer.quick_check(app_path, platform)

    console.print()

    checks = [
        ("Root/Jailbreak Detection", result.has_root_detection, "Prevents running on compromised devices"),
        ("Emulator Detection", result.has_emulator_detection, "Prevents analysis in emulators"),
        ("Debug Detection", result.has_debug_detection, "Detects attached debuggers"),
        ("Tamper Detection", result.has_tamper_detection, "Verifies app integrity"),
        ("SSL Pinning", result.has_ssl_pinning, "Prevents MITM attacks"),
        ("Code Obfuscation", result.has_obfuscation, "Makes reverse engineering harder"),
    ]

    for name, detected, description in checks:
        if detected:
            console.print(f"[green]✓[/green] {name}")
            console.print(f"  [dim]{description}[/dim]")
        else:
            console.print(f"[red]✗[/red] {name}")
            console.print(f"  [dim]{description}[/dim]")

    detected_count = sum(1 for _, d, _ in checks if d)
    console.print(f"\n[bold]Protection Coverage:[/bold] {detected_count}/{len(checks)}")

    if detected_count < len(checks) // 2:
        console.print("[red]⚠️ Application lacks basic protections![/red]")
        raise SystemExit(1)

    raise SystemExit(0)


# =============================================================================
# Comprehensive Analysis Command
# =============================================================================


@security.command(name="comprehensive")
@click.argument("app_path", type=Path)
@click.option("--platform", "-p", type=click.Choice(["android", "ios"]), required=True)
@click.option("--app-name", "-n", required=True, help="Application name")
@click.option("--source-path", "-s", type=Path, help="Source code path for SAST")
@click.option("--output", "-o", type=Path, help="Output directory for all reports")
@click.option("--target-host", "-t", type=str, help="Target host for DAST")
def comprehensive(
    app_path: Path,
    platform: str,
    app_name: str,
    source_path: Optional[Path],
    output: Optional[Path],
    target_host: Optional[str],
) -> None:
    """
    Run ALL security analyses in one comprehensive scan.

    Combines SAST, DAST, decompilation, supply chain, and runtime analysis.

    Example:
        observe security comprehensive app.apk -p android -n MyApp -o ./reports
        observe security comprehensive app.apk -p android -n MyApp -s ./src -t api.example.com
    """
    if not app_path.exists():
        console.print(f"[red]✗[/red] File not found: {app_path}")
        raise SystemExit(1)

    console.print(Panel.fit(
        "🛡️ COMPREHENSIVE SECURITY ANALYSIS\n\n"
        f"App: {app_name}\n"
        f"Platform: {platform.upper()}\n"
        f"Binary: {app_path.name}\n"
        f"Source: {source_path or 'N/A'}\n"
        f"DAST Target: {target_host or 'N/A'}",
        style="bold red"
    ))

    if output:
        output.mkdir(parents=True, exist_ok=True)

    all_findings = []
    total_critical = 0
    total_high = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # 1. Decompilation
        task1 = progress.add_task("[1/5] Decompiling binary...", total=None)
        decompiler = Decompiler()
        decompile_result = decompiler.decompile(app_path, extract_strings=True, analyze_native=True)
        all_findings.extend(decompile_result.security_findings)
        progress.update(task1, completed=True)

        # 2. SAST (if source provided or use decompiled)
        task2 = progress.add_task("[2/5] Running SAST analysis...", total=None)
        sast_analyzer = SASTAnalyzer()
        sast_source = source_path or decompile_result.output_dir
        if sast_source and Path(sast_source).exists():
            sast_result = sast_analyzer.analyze(Path(sast_source))
            for vuln in sast_result.vulnerabilities:
                if vuln.severity == "critical":
                    total_critical += 1
                elif vuln.severity == "high":
                    total_high += 1
        progress.update(task2, completed=True)

        # 3. Runtime Protection Analysis
        task3 = progress.add_task("[3/5] Analyzing runtime protections...", total=None)
        runtime_analyzer = RuntimeProtectionAnalyzer()
        runtime_result = runtime_analyzer.analyze(app_path, platform)
        progress.update(task3, completed=True)

        # 4. Supply Chain (if source provided)
        task4 = progress.add_task("[4/5] Checking supply chain...", total=None)
        if source_path and source_path.exists():
            supply_analyzer = SupplyChainAnalyzer()
            supply_result = supply_analyzer.analyze(source_path)
            for vuln in supply_result.vulnerabilities:
                if vuln.severity == "critical":
                    total_critical += 1
                elif vuln.severity == "high":
                    total_high += 1
        progress.update(task4, completed=True)

        # 5. DAST (if target provided)
        task5 = progress.add_task("[5/5] Running DAST analysis...", total=None)
        if target_host:
            dast_analyzer = DASTAnalyzer()
            dast_result = dast_analyzer.analyze(target_host)
            for finding in dast_result.findings:
                if finding.severity == "critical":
                    total_critical += 1
                elif finding.severity == "high":
                    total_high += 1
        progress.update(task5, completed=True)

    # Summary
    console.print()
    console.print(Panel.fit("📊 COMPREHENSIVE ANALYSIS SUMMARY", style="bold green"))

    summary_table = Table()
    summary_table.add_column("Analysis", style="cyan")
    summary_table.add_column("Status", style="bold")
    summary_table.add_column("Findings")

    analyses = [
        ("Binary Decompilation", "✓ Complete", f"{len(decompile_result.security_findings)} issues"),
        ("SAST", "✓ Complete" if sast_source else "⊘ Skipped", f"{len(sast_result.vulnerabilities) if sast_source else 0} vulnerabilities"),
        ("Runtime Protection", "✓ Complete", f"Score: {runtime_result.score:.0f}%"),
        ("Supply Chain", "✓ Complete" if source_path else "⊘ Skipped", f"{len(supply_result.vulnerabilities) if source_path else 0} vulnerabilities"),
        ("DAST", "✓ Complete" if target_host else "⊘ Skipped", f"{len(dast_result.findings) if target_host else 0} issues"),
    ]

    for name, status, findings in analyses:
        status_style = "green" if "✓" in status else "dim"
        summary_table.add_row(name, f"[{status_style}]{status}[/{status_style}]", findings)

    console.print(summary_table)

    # Risk assessment
    console.print(f"\n[bold]Total Critical Issues:[/bold] [red]{total_critical}[/red]")
    console.print(f"[bold]Total High Issues:[/bold] [yellow]{total_high}[/yellow]")

    if total_critical > 0:
        console.print("\n[red bold]🚨 CRITICAL RISK - Immediate remediation required![/red bold]")
    elif total_high > 5:
        console.print("\n[yellow bold]⚠️ HIGH RISK - Significant security issues found[/yellow bold]")
    elif runtime_result.score < 50:
        console.print("\n[yellow]⚠️ MODERATE RISK - Missing runtime protections[/yellow]")
    else:
        console.print("\n[green]✓ Application has reasonable security posture[/green]")

    # Save all reports
    if output:
        import json

        # Save individual reports
        with open(output / f"{app_name}_decompile.json", 'w') as f:
            json.dump(decompile_result.to_dict(), f, indent=2, default=str)

        if sast_source:
            with open(output / f"{app_name}_sast.json", 'w') as f:
                json.dump(sast_result.to_dict(), f, indent=2, default=str)

        with open(output / f"{app_name}_runtime.json", 'w') as f:
            json.dump(runtime_result.to_dict(), f, indent=2, default=str)

        if source_path:
            with open(output / f"{app_name}_supply_chain.json", 'w') as f:
                json.dump(supply_result.to_dict(), f, indent=2, default=str)

        if target_host:
            with open(output / f"{app_name}_dast.json", 'w') as f:
                json.dump(dast_result.to_dict(), f, indent=2, default=str)

        # Save combined summary
        combined = {
            "app_name": app_name,
            "platform": platform,
            "total_critical": total_critical,
            "total_high": total_high,
            "runtime_score": runtime_result.score,
            "analyses_completed": [a[0] for a in analyses if "✓" in a[1]],
        }
        with open(output / f"{app_name}_summary.json", 'w') as f:
            json.dump(combined, f, indent=2)

        console.print(f"\n[green]✓[/green] All reports saved to {output}/")

    if total_critical > 0:
        raise SystemExit(2)
    elif total_high > 0:
        raise SystemExit(1)
    raise SystemExit(0)


if __name__ == "__main__":
    security()
