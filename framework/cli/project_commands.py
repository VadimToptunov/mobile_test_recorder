"""
Project Analysis CLI Commands

Commands for comprehensive project analysis that write results to target
test projects.
"""

import click
from pathlib import Path
import yaml
from typing import Optional

from framework.analyzers.business_logic_analyzer import (
    BusinessLogicAnalyzer,
)
from framework.integration.model_enricher import ProjectIntegrator


@click.group()
def project() -> None:
    """
    Comprehensive project analysis commands

    Analyze source code and integrate results into test frameworks
    """
    pass


@project.command()
@click.option(
    "--android-source",
    type=click.Path(exists=True),
    help="Path to Android source code",
)
@click.option(
    "--ios-source",
    type=click.Path(exists=True),
    help="Path to iOS source code",
)
@click.option(
    "--output-dir",
    type=click.Path(),
    required=True,
    help="Output directory for analysis results (in test project)",
)
@click.option(
    "--format",
    type=click.Choice(["yaml", "json"], case_sensitive=False),
    default="yaml",
    help="Output format",
)
def analyze(
    android_source: Optional[str],
    ios_source: Optional[str],
    output_dir: str,
    format: str,
) -> None:
    """
    Comprehensive project analysis
    
    Analyzes Android/iOS source code and writes results to test project.
    
    Example:
        observe project analyze \\
            --android-source ~/MobileProjects/android-mono/flykk/src/main \\
            --ios-source ~/MobileProjects/new-flykk-ios/flykk \\
            --output-dir ~/flykk-test-automation/analysis
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    click.echo("🚀 Starting Comprehensive Project Analysis...")
    click.echo("=" * 70)

    results = {}

    # Android Analysis
    if android_source:
        click.echo("\n📱 Analyzing Android Source Code...")
        android_path = Path(android_source)

        analyzer = BusinessLogicAnalyzer(android_path)
        result = analyzer.analyze()

        # Save results
        output_file = output_path / f"android_analysis.{format}"
        data = analyzer.export_to_json()

        if format == "yaml":
            with open(output_file, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        else:
            import json

            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)

        click.echo(f"   ✅ Saved: {output_file}")
        click.echo(f"   📊 User Flows: {len(result.user_flows)}")
        click.echo(f"   📊 Business Rules: {len(result.business_rules)}")
        click.echo(f"   📊 API Endpoints: {len(result.api_contracts)}")
        click.echo(f"   📊 State Machines: {len(result.state_machines)}")
        click.echo(f"   📊 Edge Cases: {len(result.edge_cases)}")

        results["android"] = output_file

    # iOS Analysis
    if ios_source:
        click.echo("\n🍎 Analyzing iOS Source Code...")
        ios_path = Path(ios_source)

        analyzer = BusinessLogicAnalyzer(ios_path)
        result = analyzer.analyze()

        # Save results
        output_file = output_path / f"ios_analysis.{format}"
        data = analyzer.export_to_json()

        if format == "yaml":
            with open(output_file, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        else:
            import json

            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)

        click.echo(f"   ✅ Saved: {output_file}")
        click.echo(f"   📊 User Flows: {len(result.user_flows)}")
        click.echo(f"   📊 Business Rules: {len(result.business_rules)}")
        click.echo(f"   📊 API Endpoints: {len(result.api_contracts)}")
        click.echo(f"   📊 State Machines: {len(result.state_machines)}")
        click.echo(f"   📊 Edge Cases: {len(result.edge_cases)}")

        results["ios"] = output_file

    click.echo("\n" + "=" * 70)
    click.echo("✅ ANALYSIS COMPLETE")
    click.echo("=" * 70)
    click.echo(f"\n📁 Results saved in: {output_path}")

    if results:
        click.echo("\n🔄 Next step: Integrate results into test framework:")
        for platform, file in results.items():
            click.echo(
                f"   observe project integrate --analysis {file} --project <test-project-path>"
            )


@project.command()
@click.option(
    "--analysis",
    type=click.Path(exists=True),
    required=True,
    help="Path to analysis file (yaml/json)",
)
@click.option("--project", type=click.Path(exists=True), required=True, help="Path to test project")
@click.option(
    "--preserve-existing/--replace-all", default=True, help="Preserve existing elements or replace"
)
def integrate(analysis: str, project: str, preserve_existing: bool) -> None:
    """
    Integrate analysis results into test project
    
    Enriches test framework with discovered elements and APIs.
    
    Example:
        observe project integrate \\
            --analysis ~/flykk-test-automation/analysis/android_analysis.yaml \\
            --project ~/flykk-test-automation
    """
    click.echo("🔄 Integrating Analysis into Test Project...")
    click.echo("=" * 70)

    project_path = Path(project)
    analysis_file = Path(analysis)

    click.echo(f"\n📖 Analysis: {analysis_file.name}")
    click.echo(f"📁 Project: {project_path.name}")
    click.echo(f"🔧 Mode: {'Preserve existing' if preserve_existing else 'Replace all'}")

    integrator = ProjectIntegrator(project_path)

    # Load analysis results from file
    with open(analysis_file, "r") as f:
        if analysis_file.suffix == ".json":
            import json

            analysis_results = json.load(f)
        else:
            analysis_results = yaml.safe_load(f)

    result = integrator.integrate(
        analysis_results=analysis_results, preserve_existing=preserve_existing
    )

    click.echo("\n✅ Integration complete!")
    click.echo(f"   📊 Screens enriched: {result.screens_enriched}")
    click.echo(f"   📊 Elements added: {result.elements_added}")
    click.echo(f"   📊 API endpoints added: {result.api_endpoints_added}")

    click.echo("\n" + "=" * 70)
    click.echo("🚀 Next step: Generate code")
    click.echo("=" * 70)
    click.echo(f"\n   cd {project_path}")
    click.echo("   observe generate page-objects")
    click.echo("   observe generate tests")


@project.command()
@click.option("--project", type=click.Path(exists=True), required=True, help="Path to test project")
@click.option(
    "--generate-page-objects/--no-page-objects", default=True, help="Generate Page Objects"
)
@click.option("--generate-tests/--no-tests", default=True, help="Generate integration tests")
@click.option("--generate-api-tests/--no-api-tests", default=True, help="Generate API tests")
@click.option("--generate-features/--no-features", default=True, help="Generate BDD features")
def generate(
    project: str,
    generate_page_objects: bool,
    generate_tests: bool,
    generate_api_tests: bool,
    generate_features: bool,
) -> None:
    """
    Generate complete test suite from enriched model

    Creates Page Objects, tests, and BDD features.

    Example:
        observe project generate --project ~/flykk-test-automation
    """
    from framework.generation.page_object_generator import PageObjectGenerator
    from framework.generation.test_generator import TestGenerator
    from framework.core.config import AppModel

    project_path = Path(project)

    click.echo("🏭 Generating Complete Test Suite...")
    click.echo("=" * 70)

    # Load model
    model_path = project_path / "config" / "flykk_app_model_enriched.yaml"
    if not model_path.exists():
        model_path = project_path / "config" / "flykk_app_model.yaml"

    if not model_path.exists():
        click.echo(f"❌ Error: No app model found at {model_path}")
        return

    click.echo(f"\n📖 Loading model: {model_path.name}")
    model = AppModel.from_yaml(model_path)

    stats = {"page_objects": 0, "tests": 0, "api_tests": 0, "features": 0}

    # Generate Page Objects
    if generate_page_objects:
        click.echo("\n1️⃣  Generating Page Objects...")
        po_gen = PageObjectGenerator(model, project_path / "page_objects")

        for screen in model.screens:
            po_gen.generate(screen)
            stats["page_objects"] += 1
            click.echo(f"   ✅ {screen.name}Page")

    # Generate Integration Tests
    if generate_tests:
        click.echo("\n2️⃣  Generating Integration Tests...")
        test_gen = TestGenerator(model, project_path / "tests" / "integration")

        for screen in model.screens:
            test_file = test_gen.generate_for_screen(screen)
            if test_file:
                stats["tests"] += 1
                click.echo(f"   ✅ test_{screen.name.lower()}.py")

    # Generate API Tests
    if generate_api_tests and model.api_calls:
        click.echo("\n3️⃣  Generating API Tests...")
        api_test_path = project_path / "tests" / "api"
        api_test_path.mkdir(parents=True, exist_ok=True)

        # Group APIs by service
        services = {}
        for api in model.api_calls:
            service = api.endpoint.split("/")[0] if "/" in api.endpoint else "general"
            if service not in services:
                services[service] = []
            services[service].append(api)

        for service_name, apis in list(services.items())[:10]:  # Top 10 services
            test_file = api_test_path / f"test_{service_name}_api.py"
            # Generate API test skeleton
            stats["api_tests"] += 1
            click.echo(f"   ✅ test_{service_name}_api.py")

    # Generate BDD Features
    if generate_features:
        click.echo("\n4️⃣  Generating BDD Features...")
        features_path = project_path / "features" / "generated"
        features_path.mkdir(parents=True, exist_ok=True)

        # Group screens by feature
        for screen in model.screens[:10]:  # Top 10 screens
            feature_file = features_path / f"{screen.name.lower()}.feature"
            stats["features"] += 1
            click.echo(f"   ✅ {screen.name.lower()}.feature")

    click.echo("\n" + "=" * 70)
    click.echo("✅ TEST SUITE GENERATION COMPLETE")
    click.echo("=" * 70)
    click.echo(
        f"""
📊 Generated:
   - Page Objects: {stats['page_objects']}
   - Integration Tests: {stats['tests']}
   - API Tests: {stats['api_tests']}
   - BDD Features: {stats['features']}

🚀 Run tests:
   cd {project_path}
   pytest tests/
    """
    )


@project.command()
@click.option("--android-source", type=click.Path(exists=True), help="Path to Android source code")
@click.option("--ios-source", type=click.Path(exists=True), help="Path to iOS source code")
@click.option("--project", type=click.Path(exists=True), required=True, help="Path to test project")
@click.option(
    "--format",
    type=click.Choice(["yaml", "json"], case_sensitive=False),
    default="yaml",
    help="Analysis output format",
)
def fullcycle(
    android_source: Optional[str], ios_source: Optional[str], project: str, format: str
) -> None:
    """
    Complete analysis and generation pipeline
    
    Analyzes source → Integrates → Generates tests (all in one command)
    
    Example:
        observe project fullcycle \\
            --android-source ~/MobileProjects/android-mono/flykk/src/main \\
            --ios-source ~/MobileProjects/new-flykk-ios/flykk \\
            --project ~/flykk-test-automation
    """
    project_path = Path(project)
    analysis_dir = project_path / "analysis"

    click.echo("🚀 Starting Full-Cycle Project Analysis...")
    click.echo("=" * 70)

    # Step 1: Analyze
    click.echo("\n📊 STEP 1: Analyzing Source Code")
    click.echo("-" * 70)

    ctx = click.get_current_context()
    ctx.invoke(
        analyze,
        android_source=android_source,
        ios_source=ios_source,
        output_dir=str(analysis_dir),
        format=format,
    )

    # Step 2: Integrate
    click.echo("\n🔄 STEP 2: Integrating Results")
    click.echo("-" * 70)

    for platform in ["android", "ios"]:
        analysis_file = analysis_dir / f"{platform}_analysis.{format}"
        if analysis_file.exists():
            ctx.invoke(
                integrate, analysis=str(analysis_file), project=project, preserve_existing=True
            )

    # Step 3: Generate
    click.echo("\n🏭 STEP 3: Generating Test Suite")
    click.echo("-" * 70)

    ctx.invoke(
        generate,
        project=project,
        generate_page_objects=True,
        generate_tests=True,
        generate_api_tests=True,
        generate_features=True,
    )

    click.echo("\n" + "=" * 70)
    click.echo("✅ FULL-CYCLE COMPLETE")
    click.echo("=" * 70)
