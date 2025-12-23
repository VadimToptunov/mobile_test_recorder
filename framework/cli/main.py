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
            from framework.analyzers.android_analyzer import AndroidAnalyzer
            
            click.echo(f"\n🤖 Running Android static analyzer...")
            analyzer = AndroidAnalyzer()
            result = analyzer.analyze(source)
            
        elif platform == 'ios':
            from framework.analyzers.ios_analyzer import IOSAnalyzer
            from pathlib import Path
            
            click.echo(f"\n🍎 Running iOS static analyzer...")
            analyzer = IOSAnalyzer(project_path=Path(source))
            result = analyzer.analyze()
            
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
@click.option('--package', default='com.findemo',
              help='App package name (e.g., com.myapp)')
def start(device: str, session_name: str, package: str):
    """
    Start recording session
    
    Example:
        observe record start --device emulator-5554 --package com.myapp
    """
    from datetime import datetime
    
    session_id = session_name or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    click.echo(f"🎯 Starting recording session...")
    click.echo(f"   Session ID: {session_id}")
    click.echo(f"   Device: {device}")
    click.echo(f"   Package: {package}")
    click.echo(f"\n📱 Perform actions in the app...")
    click.echo(f"   Press Ctrl+C to stop recording\n")
    
    try:
        from framework.storage.event_store import EventStore
        import subprocess
        import time
        
        # Initialize event store
        store = EventStore()
        
        # Session will be created automatically when first event is imported
        
        # Build device path
        device_path = f'/sdcard/Android/data/{package}/files/observe/'
        
        # Start monitoring (pull events from device)
        click.echo("📡 Monitoring device for events...")
        click.echo(f"   Pulling events from: {device_path}")
        click.echo("   Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Pull event files from device
                result = subprocess.run(
                    ['adb', '-s', device, 'shell', 'ls', device_path],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    files = result.stdout.strip().split('\n')
                    for file in files:
                        if file.endswith('.json'):
                            # Pull file
                            local_path = f'/tmp/{file}'
                            subprocess.run(
                                ['adb', '-s', device, 'pull', 
                                 f'{device_path}{file}',
                                 local_path],
                                capture_output=True
                            )
                            
                            # Import to event store
                            try:
                                store.import_from_json(local_path)
                                click.echo(f"   ✅ Imported: {file}")
                                
                                # Delete from device
                                subprocess.run(
                                    ['adb', '-s', device, 'shell', 'rm',
                                     f'{device_path}{file}'],
                                    capture_output=True
                                )
                            except Exception as e:
                                click.echo(f"   ⚠️  Failed to import {file}: {e}")
                
                time.sleep(2)  # Poll every 2 seconds
                
        except KeyboardInterrupt:
            click.echo("\n\n🛑 Recording stopped by user")
            
        # Show summary
        events = store.get_events(session_id=session_id)
        click.echo(f"\n✅ Recording complete!")
        click.echo(f"   Total events: {len(events)}")
        click.echo(f"   Session ID: {session_id}")
        click.echo(f"\n💡 Next steps:")
        click.echo(f"   1. Correlate events: observe record correlate --session-id {session_id}")
        click.echo(f"   2. Build model: observe model build --session-id {session_id}")
        
    except ImportError as e:
        click.echo(f"❌ Error: {e}")
        click.echo("   Make sure all dependencies are installed")
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@record.command()
@click.option('--device', default='emulator-5554', help='Device ID')
@click.option('--package', default='com.findemo',
              help='App package name (e.g., com.myapp)')
def stop(device: str, package: str):
    """Stop current recording session and pull remaining events"""
    click.echo("🛑 Stopping recording session...")
    click.echo(f"   Device: {device}")
    click.echo(f"   Package: {package}")
    
    try:
        import subprocess
        
        # Build device path
        device_path = f'/sdcard/Android/data/{package}/files/observe/'
        
        # Pull any remaining event files
        result = subprocess.run(
            ['adb', '-s', device, 'shell', 'ls', device_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            files = result.stdout.strip().split('\n')
            click.echo(f"\n📥 Pulling {len(files)} remaining event file(s)...")
            
            for file in files:
                if file.endswith('.json'):
                    local_path = f'/tmp/{file}'
                    pull_result = subprocess.run(
                        ['adb', '-s', device, 'pull',
                         f'{device_path}{file}',
                         local_path],
                        capture_output=True
                    )
                    
                    if pull_result.returncode == 0:
                        click.echo(f"   ✅ Pulled: {file}")
                        
                        # Delete from device
                        subprocess.run(
                            ['adb', '-s', device, 'shell', 'rm',
                             f'{device_path}{file}'],
                            capture_output=True
                        )
                    else:
                        click.echo(f"   ⚠️  Failed to pull: {file}")
        
        click.echo("\n✅ Recording stopped successfully")
        click.echo("   All event files pulled from device")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")


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
    
    try:
        import yaml
        import json
        from pathlib import Path
        from framework.model.app_model import AppModel
        
        # Load models
        with open(old_model) as f:
            old_data = yaml.safe_load(f) if old_model.endswith('.yaml') else json.load(f)
        
        with open(new_model) as f:
            new_data = yaml.safe_load(f) if new_model.endswith('.yaml') else json.load(f)
        
        old_app_model = AppModel(**old_data)
        new_app_model = AppModel(**new_data)
        
        # Compare
        diff_result = {
            'summary': {
                'old_version': old_app_model.meta.app_version,
                'new_version': new_app_model.meta.app_version,
                'changes': []
            },
            'screens': {
                'added': [],
                'removed': [],
                'modified': []
            },
            'api_calls': {
                'added': [],
                'removed': [],
                'modified': []
            },
            'flows': {
                'added': [],
                'removed': [],
                'modified': []
            }
        }
        
        # Compare screens
        old_screens = set(old_app_model.screens.keys())
        new_screens = set(new_app_model.screens.keys())
        
        diff_result['screens']['added'] = list(new_screens - old_screens)
        diff_result['screens']['removed'] = list(old_screens - new_screens)
        
        for screen_name in old_screens & new_screens:
            old_screen = old_app_model.screens[screen_name]
            new_screen = new_app_model.screens[screen_name]
            
            # Compare elements
            old_elements = {e.id for e in old_screen.elements}
            new_elements = {e.id for e in new_screen.elements}
            
            if old_elements != new_elements:
                diff_result['screens']['modified'].append({
                    'name': screen_name,
                    'elements_added': list(new_elements - old_elements),
                    'elements_removed': list(old_elements - new_elements)
                })
        
        # Compare API calls
        old_apis = set(old_app_model.api_calls.keys())
        new_apis = set(new_app_model.api_calls.keys())
        
        diff_result['api_calls']['added'] = list(new_apis - old_apis)
        diff_result['api_calls']['removed'] = list(old_apis - new_apis)
        
        # Compare flows
        old_flows = {f.name for f in old_app_model.flows}
        new_flows = {f.name for f in new_app_model.flows}
        
        diff_result['flows']['added'] = list(new_flows - old_flows)
        diff_result['flows']['removed'] = list(old_flows - new_flows)
        
        # Generate summary
        total_changes = (
            len(diff_result['screens']['added']) +
            len(diff_result['screens']['removed']) +
            len(diff_result['screens']['modified']) +
            len(diff_result['api_calls']['added']) +
            len(diff_result['api_calls']['removed']) +
            len(diff_result['flows']['added']) +
            len(diff_result['flows']['removed'])
        )
        
        # Print results
        click.echo(f"\n📊 Model Comparison Results:")
        click.echo(f"   Old version: {old_app_model.meta.app_version}")
        click.echo(f"   New version: {new_app_model.meta.app_version}")
        click.echo(f"   Total changes: {total_changes}")
        
        if diff_result['screens']['added']:
            click.echo(f"\n➕ Screens Added ({len(diff_result['screens']['added'])}):")
            for screen in diff_result['screens']['added']:
                click.echo(f"   • {screen}")
        
        if diff_result['screens']['removed']:
            click.echo(f"\n➖ Screens Removed ({len(diff_result['screens']['removed'])}):")
            for screen in diff_result['screens']['removed']:
                click.echo(f"   • {screen}")
        
        if diff_result['screens']['modified']:
            click.echo(f"\n🔄 Screens Modified ({len(diff_result['screens']['modified'])}):")
            for mod in diff_result['screens']['modified']:
                click.echo(f"   • {mod['name']}")
                if mod['elements_added']:
                    click.echo(f"     ➕ Elements: {', '.join(mod['elements_added'])}")
                if mod['elements_removed']:
                    click.echo(f"     ➖ Elements: {', '.join(mod['elements_removed'])}")
        
        if diff_result['api_calls']['added']:
            click.echo(f"\n➕ API Calls Added ({len(diff_result['api_calls']['added'])}):")
            for api in diff_result['api_calls']['added']:
                click.echo(f"   • {api}")
        
        if diff_result['api_calls']['removed']:
            click.echo(f"\n➖ API Calls Removed ({len(diff_result['api_calls']['removed'])}):")
            for api in diff_result['api_calls']['removed']:
                click.echo(f"   • {api}")
        
        if diff_result['flows']['added']:
            click.echo(f"\n➕ Flows Added ({len(diff_result['flows']['added'])}):")
            for flow in diff_result['flows']['added']:
                click.echo(f"   • {flow}")
        
        if diff_result['flows']['removed']:
            click.echo(f"\n➖ Flows Removed ({len(diff_result['flows']['removed'])}):")
            for flow in diff_result['flows']['removed']:
                click.echo(f"   • {flow}")
        
        # Save to file
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(diff_result, f, indent=2)
            click.echo(f"\n💾 Diff saved to: {output}")
        
        click.echo(f"\n✅ Comparison complete")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


@model.command()
@click.argument('model_file', type=click.Path(exists=True))
def validate(model_file: str):
    """Validate app model against JSON schema"""
    click.echo(f"✔️  Validating model: {model_file}")
    
    try:
        import yaml
        import json
        from framework.model.app_model import AppModel
        from pydantic import ValidationError
        
        # Load model file
        with open(model_file) as f:
            if model_file.endswith('.yaml') or model_file.endswith('.yml'):
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        # Validate using Pydantic
        try:
            app_model = AppModel(**data)
            
            # Additional validations
            errors = []
            warnings = []
            
            # Check for screens without elements
            for screen_name, screen in app_model.screens.items():
                if not screen.elements:
                    warnings.append(f"Screen '{screen_name}' has no elements")
            
            # Check for elements without selectors
            for screen_name, screen in app_model.screens.items():
                for element in screen.elements:
                    if not element.selector:
                        errors.append(f"Element '{element.id}' in screen '{screen_name}' has no selector")
            
            # Check for API calls without endpoints
            for api_name, api_call in app_model.api_calls.items():
                if not api_call.endpoint:
                    errors.append(f"API call '{api_name}' has no endpoint")
            
            # Check for flows without steps
            for flow in app_model.flows:
                if not flow.steps:
                    errors.append(f"Flow '{flow.name}' has no steps")
                    
                # Check if flow steps reference existing screens
                for step in flow.steps:
                    screen_ref = step.get('screen')
                    if screen_ref and screen_ref not in app_model.screens:
                        errors.append(f"Flow '{flow.name}' references unknown screen '{screen_ref}'")
            
            # Check state machine
            if app_model.state_machine:
                for state in app_model.state_machine.states:
                    if state not in app_model.screens:
                        errors.append(f"State machine references unknown screen '{state}'")
            
            # Print results
            click.echo("\n📋 Validation Results:")
            
            if not errors and not warnings:
                click.echo("   ✅ Model is valid!")
                click.echo(f"\n📊 Model Statistics:")
                click.echo(f"   Screens: {len(app_model.screens)}")
                click.echo(f"   API Calls: {len(app_model.api_calls)}")
                click.echo(f"   Flows: {len(app_model.flows)}")
                
                total_elements = sum(len(s.elements) for s in app_model.screens.values())
                click.echo(f"   Total Elements: {total_elements}")
                
                if app_model.state_machine:
                    click.echo(f"   States: {len(app_model.state_machine.states)}")
                    click.echo(f"   Transitions: {len(app_model.state_machine.transitions)}")
            else:
                if errors:
                    click.echo(f"\n❌ Errors ({len(errors)}):")
                    for error in errors:
                        click.echo(f"   • {error}")
                
                if warnings:
                    click.echo(f"\n⚠️  Warnings ({len(warnings)}):")
                    for warning in warnings:
                        click.echo(f"   • {warning}")
                
                if errors:
                    click.echo("\n❌ Validation failed")
                    exit(1)
                else:
                    click.echo("\n✅ Validation passed with warnings")
        
        except ValidationError as e:
            click.echo("\n❌ Validation failed:")
            for error in e.errors():
                location = ' → '.join(str(loc) for loc in error['loc'])
                click.echo(f"   • {location}: {error['msg']}")
            exit(1)
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


@model.command()
@click.argument('model_file', type=click.Path(exists=True))
@click.option('--detailed', is_flag=True, help='Show detailed analysis')
def analyze_selectors(model_file: str, detailed: bool):
    """
    Analyze selectors in app model
    
    Example:
        observe model analyze-selectors models/app_model.yaml
    """
    click.echo(f"🔍 Analyzing selectors in model...")
    click.echo(f"   Model: {model_file}")
    
    try:
        import yaml
        import json
        from framework.model.app_model import AppModel
        from framework.selectors import SelectorOptimizer
        
        # Load model
        with open(model_file, 'r') as f:
            if model_file.endswith('.yaml') or model_file.endswith('.yml'):
                model_data = yaml.safe_load(f)
            else:
                model_data = json.load(f)
        
        app_model = AppModel(**model_data)
        optimizer = SelectorOptimizer()
        
        # Collect all selectors
        all_selectors = []
        for screen in app_model.screens.values():
            for element in screen.elements:
                if element.selector:
                    all_selectors.append(element.selector)
        
        # Analyze
        analysis = optimizer.analyze_selectors(all_selectors)
        
        # Print results
        click.echo(f"\n📊 Selector Analysis Results:")
        click.echo(f"   Total selectors: {analysis['total']}")
        
        if analysis['total'] == 0:
            click.echo("\n⚠️  No selectors found in the model.")
            return
        
        click.echo(f"   Average stability: {analysis['average_stability']:.2f}")
        
        click.echo(f"\n📈 Stability Distribution:")
        dist = analysis['stability_distribution']
        click.echo(f"   ✨ Excellent: {dist['excellent']} ({dist['excellent']/analysis['total']*100:.1f}%)")
        click.echo(f"   ✅ Good:      {dist['good']} ({dist['good']/analysis['total']*100:.1f}%)")
        click.echo(f"   ⚠️  Fair:      {dist['fair']} ({dist['fair']/analysis['total']*100:.1f}%)")
        click.echo(f"   ❌ Poor:      {dist['poor']} ({dist['poor']/analysis['total']*100:.1f}%)")
        click.echo(f"   💥 Fragile:   {dist['fragile']} ({dist['fragile']/analysis['total']*100:.1f}%)")
        
        click.echo(f"\n🎯 Strategy Distribution:")
        for strategy, count in sorted(analysis['strategy_distribution'].items(), key=lambda x: x[1], reverse=True):
            percentage = count / analysis['total'] * 100
            click.echo(f"   {strategy}: {count} ({percentage:.1f}%)")
        
        click.echo(f"\n💡 Recommendations:")
        for rec in analysis['recommendations']:
            click.echo(f"   {rec}")
        
        # Detailed analysis if requested
        if detailed:
            click.echo(f"\n🔬 Detailed Selector Analysis:")
            
            # Find problematic selectors (LOW stability)
            from framework.model.app_model import SelectorStability
            problematic = [s for s in all_selectors if s.stability == SelectorStability.LOW]
            
            if problematic:
                click.echo(f"\n⚠️  {len(problematic)} problematic selectors found:")
                for selector in problematic[:10]:  # Show first 10
                    # Determine which selector string to display
                    selector_str = selector.android or selector.ios or selector.test_id or selector.xpath or "unknown"
                    click.echo(f"\n   Selector: {selector_str}")
                    click.echo(f"   Stability: {selector.stability.value}")
                    
                    suggestions = optimizer.suggest_improvements(selector)
                    for suggestion in suggestions:
                        click.echo(f"      {suggestion}")
            
            # Check for duplicates
            duplicates = optimizer.find_duplicate_selectors(all_selectors)
            if duplicates:
                click.echo(f"\n⚠️  {len(duplicates)} duplicate selectors found:")
                for elem1, elem2 in duplicates[:5]:
                    click.echo(f"   • {elem1} and {elem2} have identical selectors")
        
        click.echo(f"\n✅ Analysis complete!")
        
    except Exception as e:
        click.echo(f"\n❌ Error analyzing selectors: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


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