"""
Main CLI entry point for Mobile Observe & Test Framework
"""

import click
from pathlib import Path
from typing import Optional
from framework import __version__


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx):
    """
    🎯 Mobile Observe & Test Framework
    
    Intelligent Mobile Testing Platform - Observe, Analyze, Automate
    """
    ctx.ensure_object(dict)


@cli.command()
@click.option('--platform', type=click.Choice(['android', 'ios']), required=True,
              help='Target platform')
@click.option('--output', type=click.Path(), default='.',
              help='Output directory for project')
def init(platform: str, output: str):
    """
    Initialize new observe project
    
    Example:
        observe init --platform android --output ./my-project
    """
    click.echo(f"🚀 Initializing {platform} observe project...")
    
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create project structure
    (output_path / "models").mkdir(exist_ok=True)
    (output_path / "tests").mkdir(exist_ok=True)
    (output_path / "sessions").mkdir(exist_ok=True)
    (output_path / "config").mkdir(exist_ok=True)
    
    # Create config file
    config_file = output_path / "config" / "observe.yaml"
    config_file.write_text(f"""
# Mobile Observe Configuration
platform: {platform}
version: "1.0"

observe_build:
  app_path: ""  # Path to observe build APK/IPA
  
test_build:
  app_path: ""  # Path to test build APK/IPA
  
appium:
  server_url: "http://localhost:4723"
  capabilities:
    platformName: {platform.capitalize()}
    automationName: {"UiAutomator2" if platform == "android" else "XCUITest"}
    deviceName: "emulator-5554"
    
model:
  output: "models/app_model.yaml"
  schema_version: "1.0.0"
  
generation:
  page_objects_output: "tests/pages"
  api_client_output: "tests/api"
  features_output: "tests/features"
""")
    
    click.echo(f"✅ Project initialized at: {output_path.absolute()}")
    click.echo(f"\nNext steps:")
    click.echo(f"  1. Update config/observe.yaml with your app paths")
    click.echo(f"  2. Run: observe analyze {platform} --source <path-to-source>")
    click.echo(f"  3. Run: observe record start")


@cli.command()
@click.argument('platform', type=click.Choice(['android', 'ios']))
@click.option('--source', type=click.Path(exists=True),
              help='Path to source code')
@click.option('--output', type=click.Path(), default='models/static_analysis.yaml',
              help='Output file for analysis results')
def analyze(platform: str, source: str, output: str):
    """
    Analyze source code (static analysis)
    
    Example:
        observe analyze android --source ./demo-app/android
    """
    click.echo(f"🔍 Analyzing {platform} source code...")
    
    if not source:
        click.echo("❌ Error: --source is required", err=True)
        return
    
    click.echo(f"📂 Source: {source}")
    click.echo(f"📄 Output: {output}")
    
    try:
        from pathlib import Path
        import yaml
        import json
        
        if platform == 'android':
            from framework.analyzers import AndroidAnalyzer
            
            click.echo(f"\n🤖 Running Android static analyzer...")
            analyzer = AndroidAnalyzer()
            result = analyzer.analyze(source)
            
        elif platform == 'ios':
            click.echo(f"\n❌ iOS static analysis not yet implemented")
            return
        else:
            click.echo(f"\n❌ Unknown platform: {platform}")
            return
        
        # Save results
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            if output.endswith('.json'):
                json.dump(result.model_dump(), f, indent=2, default=str)
            else:
                yaml.dump(result.model_dump(), f, default_flow_style=False, sort_keys=False)
        
        # Print summary
        click.echo(f"\n✅ Static analysis complete!")
        click.echo(f"\n📊 Results:")
        click.echo(f"   Files analyzed: {result.files_analyzed}")
        click.echo(f"   Screens found: {len(result.screens)}")
        click.echo(f"   UI elements found: {len(result.ui_elements)}")
        click.echo(f"   Navigation routes: {len(result.navigation)}")
        click.echo(f"   API endpoints: {len(result.api_endpoints)}")
        
        if result.errors:
            click.echo(f"\n⚠️  Errors: {len(result.errors)}")
            for error in result.errors[:5]:  # Show first 5
                click.echo(f"   • {error}")
        
        if result.warnings:
            click.echo(f"\n⚠️  Warnings: {len(result.warnings)}")
        
        click.echo(f"\n📄 Results saved to: {output_path}")
        click.echo(f"\nNext steps:")
        click.echo(f"  1. Review the analysis results")
        click.echo(f"  2. Record a session: observe record start")
        click.echo(f"  3. Merge static + dynamic: observe model build")
        
    except Exception as e:
        click.echo(f"\n❌ Error during analysis: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


@cli.group()
def record():
    """Record observe sessions"""
    pass


@record.command()
@click.option('--device', default='emulator-5554',
              help='Device ID or emulator name')
@click.option('--session-name', default=None,
              help='Custom session name')
def start(device: str, session_name: str):
    """
    Start recording session
    
    Example:
        observe record start --device emulator-5554
    """
    from datetime import datetime
    
    session_id = session_name or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    click.echo(f"🎯 Starting recording session...")
    click.echo(f"   Session ID: {session_id}")
    click.echo(f"   Device: {device}")
    click.echo(f"\n📱 Perform actions in the app...")
    click.echo(f"   Press Ctrl+C to stop recording\n")
    
    # TODO: Implement recording
    click.echo("⚠️  Recording not yet implemented")
    click.echo("   This will be available after Observe SDK is complete")


@record.command()
def stop():
    """Stop current recording session"""
    click.echo("🛑 Stopping recording session...")
    # TODO: Implement
    click.echo("⚠️  Not yet implemented")


@record.command()
@click.option('--session-id', required=True, help='Session ID to correlate')
@click.option('--output', type=click.Path(), default='correlations.json',
              help='Output file for correlation results')
def correlate(session_id: str, output: str):
    """
    Correlate events in a recorded session
    
    Example:
        observe record correlate --session-id session_20250119_142345
    """
    click.echo(f"🔗 Correlating events for session: {session_id}")
    click.echo(f"   Output: {output}")
    
    try:
        from pathlib import Path
        import json
        from framework.storage.event_store import EventStore
        from framework.correlation import EventCorrelator
        
        # Initialize event store
        store = EventStore()
        
        # Initialize correlator
        correlator = EventCorrelator(event_store=store)
        
        # Correlate events
        result = correlator.correlate_session(session_id)
        
        # Save results
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(result.model_dump(), f, indent=2, default=str)
        
        # Print summary
        click.echo(f"\n✅ Correlation complete!")
        click.echo(f"\n📊 Statistics:")
        click.echo(f"   Total UI events: {result.total_ui_events}")
        click.echo(f"   Total API events: {result.total_api_events}")
        click.echo(f"   Total Navigation events: {result.total_navigation_events}")
        click.echo(f"   ")
        click.echo(f"   UI→API correlations: {len(result.ui_to_api)}")
        click.echo(f"   API→Navigation correlations: {len(result.api_to_navigation)}")
        click.echo(f"   Complete flows: {len(result.full_flows)}")
        click.echo(f"   ")
        click.echo(f"   Correlation rate: {result.correlation_rate:.1%}")
        click.echo(f"   ")
        click.echo(f"📄 Results saved to: {output_path}")
        
    except Exception as e:
        click.echo(f"\n❌ Error during correlation: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


@cli.group()
def generate():
    """Generate test code"""
    pass


@generate.command()
@click.option('--model', type=click.Path(exists=True), required=True,
              help='Path to app model file')
@click.option('--output', type=click.Path(), default='tests/pages',
              help='Output directory for Page Objects')
@click.option('--platform', type=click.Choice(['android', 'ios', 'cross-platform']),
              default='cross-platform',
              help='Target platform')
def pages(model: str, output: str, platform: str):
    """
    Generate Page Object classes
    
    Example:
        observe generate pages --model models/app_model.yaml --output tests/pages
    """
    click.echo(f"⚡ Generating Page Objects...")
    click.echo(f"   Model: {model}")
    click.echo(f"   Output: {output}")
    click.echo(f"   Platform: {platform}")
    
    try:
        from pathlib import Path
        import yaml
        from framework.model.app_model import AppModel
        from framework.generators.page_object_gen import generate_all_page_objects
        
        # Load model
        with open(model, 'r') as f:
            if model.endswith('.yaml') or model.endswith('.yml'):
                model_data = yaml.safe_load(f)
            else:
                import json
                model_data = json.load(f)
        
        app_model = AppModel(**model_data)
        
        # Generate Page Objects - MUST pass .values() to get Screen objects, not keys
        output_path = Path(output)
        generated_files = generate_all_page_objects(list(app_model.screens.values()), output_path)
        
        click.echo(f"\n✅ Generated {len(generated_files)} Page Object files:")
        for file_path in generated_files:
            click.echo(f"   📄 {file_path}")
        
    except Exception as e:
        click.echo(f"\n❌ Error generating Page Objects: {e}", err=True)
        raise click.Abort()


@generate.command()
@click.option('--model', type=click.Path(exists=True), required=True,
              help='Path to app model file')
@click.option('--output', type=click.Path(), default='tests/api',
              help='Output directory for API clients')
def api(model: str, output: str):
    """Generate API client classes"""
    click.echo(f"⚡ Generating API clients...")
    click.echo(f"   Model: {model}")
    click.echo(f"   Output: {output}")
    
    try:
        from pathlib import Path
        import yaml
        from framework.model.app_model import AppModel
        from framework.generators.api_client_gen import generate_api_client
        
        # Load model
        with open(model, 'r') as f:
            if model.endswith('.yaml') or model.endswith('.yml'):
                model_data = yaml.safe_load(f)
            else:
                import json
                model_data = json.load(f)
        
        app_model = AppModel(**model_data)
        
        # Generate API client - MUST pass .values() to get APICall objects, not keys
        output_path = Path(output) / "api_client.py"
        generated_file = generate_api_client(list(app_model.api_calls.values()), output_path)
        
        click.echo(f"\n✅ Generated API client:")
        click.echo(f"   📄 {generated_file}")
        
    except Exception as e:
        click.echo(f"\n❌ Error generating API client: {e}", err=True)
        raise click.Abort()


@generate.command()
@click.option('--model', type=click.Path(exists=True), required=True,
              help='Path to app model file')
@click.option('--output', type=click.Path(), default='tests/features',
              help='Output directory for feature files')
def features(model: str, output: str):
    """Generate BDD feature files"""
    click.echo(f"⚡ Generating BDD features...")
    click.echo(f"   Model: {model}")
    click.echo(f"   Output: {output}")
    
    try:
        from pathlib import Path
        import yaml
        from framework.model.app_model import AppModel
        from framework.generators.bdd_gen import generate_all_features
        
        # Load model
        with open(model, 'r') as f:
            if model.endswith('.yaml') or model.endswith('.yml'):
                model_data = yaml.safe_load(f)
            else:
                import json
                model_data = json.load(f)
        
        app_model = AppModel(**model_data)
        
        # Generate BDD features
        output_path = Path(output)
        generated_files = generate_all_features(app_model.flows, output_path)
        
        click.echo(f"\n✅ Generated {len(generated_files)} feature files:")
        for file_path in generated_files:
            click.echo(f"   📄 {file_path}")
        
    except Exception as e:
        click.echo(f"\n❌ Error generating BDD features: {e}", err=True)
        raise click.Abort()


@cli.group()
def model():
    """App model operations"""
    pass


@model.command()
@click.argument('old_model', type=click.Path(exists=True))
@click.argument('new_model', type=click.Path(exists=True))
@click.option('--output', type=click.Path(), default='model_diff.md',
              help='Output file for diff report')
def diff(old_model: str, new_model: str, output: str):
    """
    Compare two app model versions
    
    Example:
        observe model diff model_v1.yaml model_v2.yaml
    """
    click.echo(f"🔄 Comparing models...")
    click.echo(f"   Old: {old_model}")
    click.echo(f"   New: {new_model}")
    click.echo(f"   Output: {output}")
    
    # TODO: Implement diff
    click.echo("\n⚠️  Model diff not yet implemented")


@model.command()
@click.argument('model_file', type=click.Path(exists=True))
def validate(model_file: str):
    """Validate app model against JSON schema"""
    click.echo(f"✔️  Validating model: {model_file}")
    # TODO: Implement validation
    click.echo("⚠️  Not yet implemented")


@model.command()
@click.option('--session-id', required=True, help='Session ID to build from')
@click.option('--app-version', required=True, help='Application version')
@click.option('--platform', type=click.Choice(['android', 'ios']), default='android',
              help='Target platform')
@click.option('--output', type=click.Path(), default='models/app_model.yaml',
              help='Output file for generated model')
@click.option('--correlations', type=click.Path(exists=True),
              help='Pre-computed correlations JSON file (optional)')
def build(session_id: str, app_version: str, platform: str, output: str, correlations: Optional[str]):
    """
    Build AppModel from recorded session
    
    Example:
        observe model build --session-id session_20250119_142345 --app-version 1.0.0
    """
    click.echo(f"🏗️  Building AppModel from session...")
    click.echo(f"   Session: {session_id}")
    click.echo(f"   App Version: {app_version}")
    click.echo(f"   Platform: {platform}")
    click.echo(f"   Output: {output}")
    
    try:
        from pathlib import Path
        import yaml
        import json
        from framework.storage.event_store import EventStore
        from framework.model_builder import ModelBuilder
        from framework.model.app_model import Platform
        from framework.correlation import CorrelationResult
        
        # Initialize store and builder
        store = EventStore()
        builder = ModelBuilder(event_store=store)
        
        # Load correlations if provided
        correlation_result = None
        if correlations:
            click.echo(f"\n📊 Loading correlations from: {correlations}")
            with open(correlations, 'r') as f:
                corr_data = json.load(f)
                correlation_result = CorrelationResult(**corr_data)
        
        # Map platform string to enum
        platform_enum = Platform.ANDROID if platform == 'android' else Platform.IOS
        
        # Build model
        click.echo(f"\n🔨 Building model...")
        app_model = builder.build_from_session(
            session_id=session_id,
            app_version=app_version,
            platform=platform_enum,
            correlation_result=correlation_result
        )
        
        # Save model
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            if output.endswith('.json'):
                json.dump(app_model.model_dump(), f, indent=2, default=str)
            else:
                yaml.dump(app_model.model_dump(), f, default_flow_style=False, sort_keys=False)
        
        # Print summary
        click.echo(f"\n✅ AppModel built successfully!")
        click.echo(f"\n📊 Model Statistics:")
        click.echo(f"   Screens: {len(app_model.screens)}")
        click.echo(f"   API Calls: {len(app_model.api_calls)}")
        click.echo(f"   Flows: {len(app_model.flows)}")
        
        if app_model.state_machine:
            click.echo(f"   States: {len(app_model.state_machine.states)}")
            click.echo(f"   Transitions: {len(app_model.state_machine.transitions)}")
        
        click.echo(f"\n📄 Model saved to: {output_path}")
        click.echo(f"\nNext steps:")
        click.echo(f"  1. Review the generated model")
        click.echo(f"  2. Generate tests: observe generate pages --model {output}")
        
    except Exception as e:
        click.echo(f"\n❌ Error building model: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


@cli.command()
def info():
    """Show framework information"""
    click.echo(f"""
🎯 Mobile Observe & Test Framework v{__version__}

📦 Installation:
   pip install -e .

📚 Documentation:
   https://github.com/vadimtoptunov/mobile-test-recorder

🚀 Quick Start:
   1. observe init --platform android
   2. observe analyze android --source ./app
   3. observe record start
   4. observe generate pages --model models/app_model.yaml

📋 Available Commands:
   init       - Initialize new project
   analyze    - Static code analysis
   record     - Record observe sessions
   generate   - Generate test code
   model      - Model operations
   info       - This information

💡 Examples:
   observe init --platform android --output ./my-project
   observe record start --device emulator-5554
   observe generate pages --model app_model.yaml
""")


if __name__ == '__main__':
    cli()