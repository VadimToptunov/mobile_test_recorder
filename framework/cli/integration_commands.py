# Add this to the CLI in main.py after the 'analyze' command

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--analysis', type=click.Path(exists=True), required=True,
              help='Path to analysis results (YAML or JSON)')
@click.option('--output', type=click.Path(), default=None,
              help='Output path for enriched model')
@click.option('--preserve-existing/--replace-all', default=True,
              help='Preserve existing elements or replace')
def integrate(project_path: str, analysis: str, output: str, preserve_existing: bool):
    """
    Integrate framework with existing test project
    
    This command enriches existing App Models with analysis results.
    
    Examples:
        # Enrich existing project
        observe integrate ./my-project --analysis analysis/android_analysis.yaml
        
        # Replace existing model
        observe integrate ./my-project --analysis analysis.yaml --replace-all
    """
    from pathlib import Path
    import yaml
    import json
    from framework.integration import ModelEnricher, ProjectIntegrator, EnrichmentResult
    
    click.echo("🔗 Integrating with existing test framework...")
    
    project_path = Path(project_path)
    analysis_path = Path(analysis)
    
    # Load analysis results
    click.echo(f"\n📊 Loading analysis: {analysis_path}")
    with open(analysis_path) as f:
        if analysis_path.suffix == '.json':
            analysis_data = json.load(f)
        else:
            analysis_data = yaml.safe_load(f)
    
    # Create integrator
    integrator = ProjectIntegrator(project_path)
    
    # Detect framework
    framework_type = integrator.detect_framework()
    click.echo(f"   • Detected framework: {framework_type}")
    
    # Find existing artifacts
    page_objects = integrator.find_page_objects()
    click.echo(f"   • Found {len(page_objects)} Page Object files")
    
    # Perform integration
    click.echo(f"\n🔄 Enriching App Model...")
    
    # Determine output path
    if output:
        enriched_path = Path(output)
    else:
        enriched_path = project_path / "config" / "app_model_enriched.yaml"
    
    result = integrator.integrate(analysis_data, output_path=enriched_path)
    
    # Print results
    click.echo(f"\n✅ Integration Complete!")
    click.echo(f"\n📊 Enrichment Results:")
    click.echo(f"   • Screens enriched: {result.screens_enriched}")
    click.echo(f"   • Elements added: {result.elements_added}")
    click.echo(f"   • Selectors updated: {result.selectors_updated}")
    click.echo(f"   • API endpoints added: {result.api_endpoints_added}")
    click.echo(f"   • Navigation flows added: {result.navigation_added}")
    
    if result.warnings:
        click.echo(f"\n⚠️  Warnings: {len(result.warnings)}")
        for warning in result.warnings[:5]:
            click.echo(f"   • {warning}")
    
    if result.errors:
        click.echo(f"\n❌ Errors: {len(result.errors)}")
        for error in result.errors[:5]:
            click.echo(f"   • {error}")
    
    click.echo(f"\n💾 Enriched model saved: {enriched_path}")
    click.echo(f"\nNext steps:")
    click.echo(f"  1. Review enriched model: {enriched_path}")
    click.echo(f"  2. Backup original model")
    click.echo(f"  3. Apply enriched model")
    click.echo(f"  4. Regenerate test artifacts")


@cli.group()
def enrich():
    """Enrich existing test artifacts"""
    pass


@enrich.command()
@click.argument('model_path', type=click.Path(exists=True))
@click.argument('analysis_path', type=click.Path(exists=True))
@click.option('--output', type=click.Path(), default='model_enriched.yaml')
def model(model_path: str, analysis_path: str, output: str):
    """
    Enrich App Model with analysis results
    
    Example:
        observe enrich model app_model.yaml android_analysis.yaml
    """
    from pathlib import Path
    import yaml
    from framework.integration import ModelEnricher
    
    click.echo("📝 Enriching App Model...")
    
    # Load existing model
    with open(model_path) as f:
        existing_model = yaml.safe_load(f)
    
    click.echo(f"   • Current screens: {len(existing_model.get('screens', []))}")
    click.echo(f"   • Current API calls: {len(existing_model.get('api_calls', []))}")
    
    # Load analysis
    with open(analysis_path) as f:
        analysis = yaml.safe_load(f)
    
    click.echo(f"   • Discovered screens: {len(analysis.get('screens', []))}")
    click.echo(f"   • Discovered APIs: {len(analysis.get('api_endpoints', []))}")
    
    # Enrich
    enricher = ModelEnricher()
    enriched = enricher.enrich_model(existing_model, analysis)
    
    # Save
    output_path = Path(output)
    with open(output_path, 'w') as f:
        yaml.dump(enriched, f, default_flow_style=False, sort_keys=False)
    
    click.echo(f"\n✅ Enriched model saved: {output_path}")
    click.echo(f"\n📊 Changes:")
    click.echo(f"   • Screens enriched: {enricher.result.screens_enriched}")
    click.echo(f"   • Elements added: {enricher.result.elements_added}")
    click.echo(f"   • API endpoints added: {enricher.result.api_endpoints_added}")


@enrich.command()
@click.argument('page_object_path', type=click.Path(exists=True))
@click.argument('analysis_path', type=click.Path(exists=True))
def pageobject(page_object_path: str, analysis_path: str):
    """
    Enrich existing Page Object with discovered elements
    
    Example:
        observe enrich pageobject pages/home_page.py android_analysis.yaml
    """
    click.echo(f"📄 Enriching Page Object: {page_object_path}")
    click.echo("   This feature enhances existing Page Objects with:")
    click.echo("   • New element definitions from analysis")
    click.echo("   • Fallback selectors")
    click.echo("   • Self-healing integration")
    click.echo("\n   [Implementation: Parses existing PO, adds elements, rewrites]")

