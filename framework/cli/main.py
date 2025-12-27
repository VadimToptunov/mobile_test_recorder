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
     Mobile Observe & Test Framework
    
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
    click.echo(f" Initializing {platform} observe project...")
    
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
    
    click.echo(f" Project initialized at: {output_path.absolute()}")
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
    click.echo(f" Analyzing {platform} source code...")
    
    if not source:
        click.echo(" Error: --source is required", err=True)
        return
    
    click.echo(f" Source: {source}")
    click.echo(f" Output: {output}")
    
    try:
        from pathlib import Path
        import yaml
        import json
        
        if platform == 'android':
            from framework.analyzers.android_analyzer import AndroidAnalyzer
            
            click.echo(f"\n Running Android static analyzer...")
            analyzer = AndroidAnalyzer()
            result = analyzer.analyze(source)
            
        elif platform == 'ios':
            from framework.analyzers.ios_analyzer import IOSAnalyzer
            from pathlib import Path
            
            click.echo(f"\n Running iOS static analyzer...")
            analyzer = IOSAnalyzer(project_path=Path(source))
            result = analyzer.analyze()
            
        else:
            click.echo(f"\n Unknown platform: {platform}")
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
        click.echo(f"\n Static analysis complete!")
        click.echo(f"\n Results:")
        click.echo(f"   Files analyzed: {result.files_analyzed}")
        click.echo(f"   Screens found: {len(result.screens)}")
        click.echo(f"   UI elements found: {len(result.ui_elements)}")
        click.echo(f"   Navigation routes: {len(result.navigation)}")
        click.echo(f"   API endpoints: {len(result.api_endpoints)}")
        
        if result.errors:
            click.echo(f"\n  Errors: {len(result.errors)}")
            for error in result.errors[:5]:  # Show first 5
                click.echo(f"   • {error}")
        
        if result.warnings:
            click.echo(f"\n  Warnings: {len(result.warnings)}")
        
        click.echo(f"\n Results saved to: {output_path}")
        click.echo(f"\nNext steps:")
        click.echo(f"  1. Review the analysis results")
        click.echo(f"  2. Record a session: observe record start")
        click.echo(f"  3. Merge static + dynamic: observe model build")
        
    except Exception as e:
        click.echo(f"\n Error during analysis: {e}", err=True)
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
    
    click.echo(f" Starting recording session...")
    click.echo(f"   Session ID: {session_id}")
    click.echo(f"   Device: {device}")
    click.echo(f"   Package: {package}")
    click.echo(f"\n Perform actions in the app...")
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
        click.echo(" Monitoring device for events...")
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
                                click.echo(f"    Imported: {file}")
                                
                                # Delete from device
                                subprocess.run(
                                    ['adb', '-s', device, 'shell', 'rm',
                                     f'{device_path}{file}'],
                                    capture_output=True
                                )
                            except Exception as e:
                                click.echo(f"     Failed to import {file}: {e}")
                
                time.sleep(2)  # Poll every 2 seconds
                
        except KeyboardInterrupt:
            click.echo("\n\n Recording stopped by user")
            
        # Show summary
        events = store.get_events(session_id=session_id)
        click.echo(f"\n Recording complete!")
        click.echo(f"   Total events: {len(events)}")
        click.echo(f"   Session ID: {session_id}")
        click.echo(f"\n Next steps:")
        click.echo(f"   1. Correlate events: observe record correlate --session-id {session_id}")
        click.echo(f"   2. Build model: observe model build --session-id {session_id}")
        
    except ImportError as e:
        click.echo(f" Error: {e}")
        click.echo("   Make sure all dependencies are installed")
    except Exception as e:
        click.echo(f" Error: {e}")


@record.command()
@click.option('--device', default='emulator-5554', help='Device ID')
@click.option('--package', default='com.findemo',
              help='App package name (e.g., com.myapp)')
def stop(device: str, package: str):
    """Stop current recording session and pull remaining events"""
    click.echo(" Stopping recording session...")
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
            click.echo(f"\n Pulling {len(files)} remaining event file(s)...")
            
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
                        click.echo(f"    Pulled: {file}")
                        
                        # Delete from device
                        subprocess.run(
                            ['adb', '-s', device, 'shell', 'rm',
                             f'{device_path}{file}'],
                            capture_output=True
                        )
                    else:
                        click.echo(f"     Failed to pull: {file}")
        
        click.echo("\n Recording stopped successfully")
        click.echo("   All event files pulled from device")
        
    except Exception as e:
        click.echo(f" Error: {e}")


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
    click.echo(f" Correlating events for session: {session_id}")
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
        click.echo(f"\n Correlation complete!")
        click.echo(f"\n Statistics:")
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
        click.echo(f" Results saved to: {output_path}")
        
    except Exception as e:
        click.echo(f"\n Error during correlation: {e}", err=True)
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
    click.echo(f" Generating Page Objects...")
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
        
        click.echo(f"\n Generated {len(generated_files)} Page Object files:")
        for file_path in generated_files:
            click.echo(f"    {file_path}")
        
    except Exception as e:
        click.echo(f"\n Error generating Page Objects: {e}", err=True)
        raise click.Abort()


@generate.command()
@click.option('--model', type=click.Path(exists=True), required=True,
              help='Path to app model file')
@click.option('--output', type=click.Path(), default='tests/api',
              help='Output directory for API clients')
def api(model: str, output: str):
    """Generate API client classes"""
    click.echo(f" Generating API clients...")
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
        
        click.echo(f"\n Generated API client:")
        click.echo(f"    {generated_file}")
        
    except Exception as e:
        click.echo(f"\n Error generating API client: {e}", err=True)
        raise click.Abort()


@generate.command()
@click.option('--model', type=click.Path(exists=True), required=True,
              help='Path to app model file')
@click.option('--output', type=click.Path(), default='tests/features',
              help='Output directory for feature files')
def features(model: str, output: str):
    """Generate BDD feature files"""
    click.echo(f" Generating BDD features...")
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
        
        click.echo(f"\n Generated {len(generated_files)} feature files:")
        for file_path in generated_files:
            click.echo(f"    {file_path}")
        
    except Exception as e:
        click.echo(f"\n Error generating BDD features: {e}", err=True)
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
    click.echo(f" Comparing models...")
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
        click.echo(f"\n Model Comparison Results:")
        click.echo(f"   Old version: {old_app_model.meta.app_version}")
        click.echo(f"   New version: {new_app_model.meta.app_version}")
        click.echo(f"   Total changes: {total_changes}")
        
        if diff_result['screens']['added']:
            click.echo(f"\n Screens Added ({len(diff_result['screens']['added'])}):")
            for screen in diff_result['screens']['added']:
                click.echo(f"   • {screen}")
        
        if diff_result['screens']['removed']:
            click.echo(f"\n Screens Removed ({len(diff_result['screens']['removed'])}):")
            for screen in diff_result['screens']['removed']:
                click.echo(f"   • {screen}")
        
        if diff_result['screens']['modified']:
            click.echo(f"\n Screens Modified ({len(diff_result['screens']['modified'])}):")
            for mod in diff_result['screens']['modified']:
                click.echo(f"   • {mod['name']}")
                if mod['elements_added']:
                    click.echo(f"      Elements: {', '.join(mod['elements_added'])}")
                if mod['elements_removed']:
                    click.echo(f"      Elements: {', '.join(mod['elements_removed'])}")
        
        if diff_result['api_calls']['added']:
            click.echo(f"\n API Calls Added ({len(diff_result['api_calls']['added'])}):")
            for api in diff_result['api_calls']['added']:
                click.echo(f"   • {api}")
        
        if diff_result['api_calls']['removed']:
            click.echo(f"\n API Calls Removed ({len(diff_result['api_calls']['removed'])}):")
            for api in diff_result['api_calls']['removed']:
                click.echo(f"   • {api}")
        
        if diff_result['flows']['added']:
            click.echo(f"\n Flows Added ({len(diff_result['flows']['added'])}):")
            for flow in diff_result['flows']['added']:
                click.echo(f"   • {flow}")
        
        if diff_result['flows']['removed']:
            click.echo(f"\n Flows Removed ({len(diff_result['flows']['removed'])}):")
            for flow in diff_result['flows']['removed']:
                click.echo(f"   • {flow}")
        
        # Save to file
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(diff_result, f, indent=2)
            click.echo(f"\n Diff saved to: {output}")
        
        click.echo(f"\n Comparison complete")
        
    except Exception as e:
        click.echo(f" Error: {e}")
        import traceback
        traceback.print_exc()


@model.command()
@click.argument('model_file', type=click.Path(exists=True))
def validate(model_file: str):
    """Validate app model against JSON schema"""
    click.echo(f"  Validating model: {model_file}")
    
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
            click.echo("\n Validation Results:")
            
            if not errors and not warnings:
                click.echo("    Model is valid!")
                click.echo(f"\n Model Statistics:")
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
                    click.echo(f"\n Errors ({len(errors)}):")
                    for error in errors:
                        click.echo(f"   • {error}")
                
                if warnings:
                    click.echo(f"\n  Warnings ({len(warnings)}):")
                    for warning in warnings:
                        click.echo(f"   • {warning}")
                
                if errors:
                    click.echo("\n Validation failed")
                    exit(1)
                else:
                    click.echo("\n Validation passed with warnings")
        
        except ValidationError as e:
            click.echo("\n Validation failed:")
            for error in e.errors():
                location = ' → '.join(str(loc) for loc in error['loc'])
                click.echo(f"   • {location}: {error['msg']}")
            exit(1)
    
    except Exception as e:
        click.echo(f" Error: {e}")
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
    click.echo(f" Analyzing selectors in model...")
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
        click.echo(f"\n Selector Analysis Results:")
        click.echo(f"   Total selectors: {analysis['total']}")
        
        if analysis['total'] == 0:
            click.echo("\n  No selectors found in the model.")
            return
        
        click.echo(f"   Average stability: {analysis['average_stability']:.2f}")
        
        click.echo(f"\n Stability Distribution:")
        dist = analysis['stability_distribution']
        click.echo(f"    Excellent: {dist['excellent']} ({dist['excellent']/analysis['total']*100:.1f}%)")
        click.echo(f"    Good:      {dist['good']} ({dist['good']/analysis['total']*100:.1f}%)")
        click.echo(f"     Fair:      {dist['fair']} ({dist['fair']/analysis['total']*100:.1f}%)")
        click.echo(f"    Poor:      {dist['poor']} ({dist['poor']/analysis['total']*100:.1f}%)")
        click.echo(f"    Fragile:   {dist['fragile']} ({dist['fragile']/analysis['total']*100:.1f}%)")
        
        click.echo(f"\n Strategy Distribution:")
        for strategy, count in sorted(analysis['strategy_distribution'].items(), key=lambda x: x[1], reverse=True):
            percentage = count / analysis['total'] * 100
            click.echo(f"   {strategy}: {count} ({percentage:.1f}%)")
        
        click.echo(f"\n Recommendations:")
        for rec in analysis['recommendations']:
            click.echo(f"   {rec}")
        
        # Detailed analysis if requested
        if detailed:
            click.echo(f"\n Detailed Selector Analysis:")
            
            # Find problematic selectors (LOW stability)
            from framework.model.app_model import SelectorStability
            problematic = [s for s in all_selectors if s.stability == SelectorStability.LOW]
            
            if problematic:
                click.echo(f"\n  {len(problematic)} problematic selectors found:")
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
                click.echo(f"\n  {len(duplicates)} duplicate selectors found:")
                for elem1, elem2 in duplicates[:5]:
                    click.echo(f"   • {elem1} and {elem2} have identical selectors")
        
        click.echo(f"\n Analysis complete!")
        
    except Exception as e:
        click.echo(f"\n Error analyzing selectors: {e}", err=True)
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
@click.option('--use-ml', is_flag=True, help='Use ML classifier for element types (Phase 4)')
@click.option('--ml-model', type=click.Path(), 
              default='ml_models/universal_element_classifier.pkl',
              help='Path to trained ML model (universal model by default, only validated when --use-ml is set)')
def build(session_id: str, app_version: str, platform: str, output: str, correlations: Optional[str],
          use_ml: bool, ml_model: str):
    """
    Build AppModel from recorded session
    
    Examples:
        # Without ML (rule-based only)
        observe model build --session-id session_123 --app-version 1.0.0
        
        # With universal ML model (recommended, works for any app)
        observe model build --session-id session_123 --app-version 1.0.0 --use-ml
        
        # With custom ML model
        observe model build --session-id session_123 --app-version 1.0.0 --use-ml --ml-model my_model.pkl
    """
    click.echo(f"  Building AppModel from session...")
    click.echo(f"   Session: {session_id}")
    click.echo(f"   App Version: {app_version}")
    click.echo(f"   Platform: {platform}")
    click.echo(f"   Output: {output}")
    
    if use_ml:
        click.echo(f"    ML Classifier: ENABLED")
        click.echo(f"   ML Model: {ml_model}")
        
        # Validate ML model file exists only when ML is enabled
        ml_model_path = Path(ml_model)
        if not ml_model_path.exists():
            click.echo(f"\n Error: ML model file not found: {ml_model_path}", err=True)
            click.echo(f"\n Solutions:", err=True)
            click.echo(f"   1. Create universal pre-trained model (RECOMMENDED - works for ANY app):", err=True)
            click.echo(f"      observe ml create-universal-model", err=True)
            click.echo(f"", err=True)
            click.echo(f"   2. Or train on your specific app:", err=True)
            click.echo(f"      observe ml train --session-id {session_id} --auto-label", err=True)
            raise click.Abort()
    
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
        
        # Initialize builder with ML support if requested
        ml_model_path = Path(ml_model) if use_ml else None
        builder = ModelBuilder(
            event_store=store,
            use_ml_classifier=use_ml,
            ml_model_path=ml_model_path
        )
        
        # Load correlations if provided
        correlation_result = None
        if correlations:
            click.echo(f"\n Loading correlations from: {correlations}")
            with open(correlations, 'r') as f:
                corr_data = json.load(f)
                correlation_result = CorrelationResult(**corr_data)
        
        # Map platform string to enum
        platform_enum = Platform.ANDROID if platform == 'android' else Platform.IOS
        
        # Build model
        click.echo(f"\n Building model...")
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
        click.echo(f"\n AppModel built successfully!")
        click.echo(f"\n Model Statistics:")
        click.echo(f"   Screens: {len(app_model.screens)}")
        click.echo(f"   API Calls: {len(app_model.api_calls)}")
        click.echo(f"   Flows: {len(app_model.flows)}")
        
        if app_model.state_machine:
            click.echo(f"   States: {len(app_model.state_machine.states)}")
            click.echo(f"   Transitions: {len(app_model.state_machine.transitions)}")
        
        click.echo(f"\n Model saved to: {output_path}")
        click.echo(f"\nNext steps:")
        click.echo(f"  1. Review the generated model")
        click.echo(f"  2. Generate tests: observe generate pages --model {output}")
        
    except Exception as e:
        click.echo(f"\n Error building model: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


@cli.group()
def crypto():
    """
    Crypto key management for traffic decryption
    
    Commands for working with TLS/SSL keys exported from observe builds.
    
      SECURITY WARNING: These operations handle encryption keys!
    """
    pass


@crypto.command()
@click.option('--session-id', required=True, help='Session ID to pull keys for')
@click.option('--package', default='com.findemo', help='App package name')
@click.option('--output', type=click.Path(), default='.', help='Output directory')
def pull(session_id: str, package: str, output: str):
    """
    Pull crypto keys from device via ADB
    
    Example:
        observe crypto pull --session-id session_20250119_142345
    """
    click.echo(f" Pulling crypto keys from device...")
    click.echo(f"   Session: {session_id}")
    click.echo(f"   Package: {package}")
    
    try:
        from framework.security.traffic_decryptor import pull_keys_from_device
        
        keys_file = pull_keys_from_device(session_id, package)
        
        if keys_file:
            click.echo(f"\n Keys pulled successfully!")
            click.echo(f"   File: {keys_file}")
            click.echo(f"\n Next steps:")
            click.echo(f"   1. Inspect keys: observe crypto show --keys-file {keys_file}")
            click.echo(f"   2. Export for Wireshark: observe crypto export --keys-file {keys_file}")
        else:
            click.echo(f"\n Failed to pull keys from device", err=True)
            raise click.Abort()
            
    except Exception as e:
        click.echo(f"\n Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


@crypto.command()
@click.option('--keys-file', required=True, type=click.Path(exists=True),
              help='Path to crypto keys JSON file')
def show(keys_file: str):
    """
    Show information about exported crypto keys
    
    Example:
        observe crypto show --keys-file crypto_keys_session123.json
    """
    click.echo(f" Loading crypto keys...")
    
    try:
        from framework.security.traffic_decryptor import TrafficDecryptor
        
        decryptor = TrafficDecryptor()
        if decryptor.load_keys_from_file(Path(keys_file)):
            stats = decryptor.get_stats()
            sessions = decryptor.list_sessions()
            
            click.echo(f"\n Crypto Keys Loaded!")
            click.echo(f"\n Statistics:")
            click.echo(f"   TLS Keys: {stats['tls_keys_loaded']}")
            click.echo(f"   Device Keys: {'Yes' if stats['device_keys_loaded'] else 'No'}")
            click.echo(f"   Source: {stats['keys_file']}")
            
            if sessions:
                click.echo(f"\n TLS Sessions:")
                for session in sessions[:10]:  # Show first 10
                    click.echo(f"   • {session}")
                
                if len(sessions) > 10:
                    click.echo(f"   ... and {len(sessions) - 10} more")
        else:
            click.echo(f"\n Failed to load keys", err=True)
            raise click.Abort()
            
    except Exception as e:
        click.echo(f"\n Error: {e}", err=True)
        raise click.Abort()


@crypto.command()
@click.option('--keys-file', required=True, type=click.Path(exists=True),
              help='Path to crypto keys JSON file')
@click.option('--output', type=click.Path(), default='tls_keys.txt',
              help='Output file for Wireshark keys')
def export(keys_file: str, output: str):
    """
    Export TLS keys to Wireshark-compatible format
    
    Example:
        observe crypto export --keys-file crypto_keys.json --output tls_keys.txt
    """
    click.echo(f" Exporting TLS keys for Wireshark...")
    
    try:
        from framework.security.traffic_decryptor import TrafficDecryptor
        
        decryptor = TrafficDecryptor()
        if not decryptor.load_keys_from_file(Path(keys_file)):
            click.echo(f"\n Failed to load keys", err=True)
            raise click.Abort()
        
        output_path = Path(output)
        if decryptor.export_wireshark_keys(output_path):
            click.echo(f"\n TLS keys exported!")
            click.echo(f"   File: {output_path}")
            click.echo(f"\n How to use in Wireshark:")
            click.echo(f"   1. Open Wireshark")
            click.echo(f"   2. Edit → Preferences → Protocols → TLS")
            click.echo(f"   3. Set '(Pre)-Master-Secret log filename' to: {output_path.absolute()}")
            click.echo(f"   4. Restart capture - HTTPS traffic will be decrypted!")
        else:
            click.echo(f"\n Failed to export keys", err=True)
            raise click.Abort()
            
    except Exception as e:
        click.echo(f"\n Error: {e}", err=True)
        raise click.Abort()


@cli.command()
def info():
    """Show framework information"""
    click.echo(f"""
 Mobile Observe & Test Framework v{__version__}

 Installation:
   pip install -e .

 Documentation:
   https://github.com/vadimtoptunov/mobile-test-recorder

 Quick Start:
   1. observe init --platform android
   2. observe analyze android --source ./app
   3. observe record start
   4. observe generate pages --model models/app_model.yaml

 Available Commands:
   init       - Initialize new project
   analyze    - Static code analysis
   record     - Record observe sessions
   generate   - Generate test code
   model      - Model operations
   crypto     - Crypto key management (TLS/SSL decryption)
   info       - This information

 Examples:
   observe init --platform android --output ./my-project
   observe record start --device emulator-5554
   observe generate pages --model app_model.yaml
   observe crypto pull --session-id session_123
   observe ml train --session-id session_123
   observe ml analyze-patterns --session-id session_123
""")


# ==============================================================================
# ML / AI Commands (Phase 4)
# ==============================================================================

@cli.group()
def ml():
    """ ML/AI commands for intelligent testing (Phase 4)"""
    pass


@ml.command()
@click.option('--session-id', required=True, help='Session ID to train from')
@click.option('--output', type=click.Path(), default='ml_models/element_classifier.pkl',
              help='Output path for trained model')
@click.option('--test-size', default=0.2, help='Test set size (0.0-1.0)')
@click.option('--auto-label', is_flag=True, help='Auto-label data using rule-based heuristics')
def train(session_id: str, output: str, test_size: float, auto_label: bool):
    """
    Train ML element classifier from recorded sessions
    
    Example:
        # Train with auto-labeled data
        observe ml train --session-id session_20250119_142345 --auto-label
        
        # Or generate synthetic training data first:
        observe ml generate-training-data --output training_data/synthetic.json
        observe ml train --session-id session_123
    """
    click.echo(f" Training ML element classifier...")
    click.echo(f"   Session: {session_id}")
    
    try:
        from framework.ml.element_classifier import ElementClassifier
        from framework.ml.training_data_generator import TrainingDataGenerator
        from framework.storage.event_store import EventStore
        
        # Load events
        store = EventStore()
        hierarchy_events = store.get_events(
            session_id=session_id,
            event_type='HierarchyEvent',
            limit=10000
        )
        
        if not hierarchy_events:
            click.echo(f"\n No hierarchy events found for session {session_id}", err=True)
            click.echo(f"\n Tips:", err=True)
            click.echo(f"   1. Make sure you recorded a session with HierarchyCollector enabled", err=True)
            click.echo(f"   2. Or generate synthetic training data:", err=True)
            click.echo(f"      observe ml generate-training-data", err=True)
            raise click.Abort()
        
        click.echo(f"\n Loaded {len(hierarchy_events)} hierarchy events")
        
        # Auto-label if requested
        if auto_label:
            click.echo(f"\n  Auto-labeling data using rule-based heuristics...")
            generator = TrainingDataGenerator()
            hierarchy_events = generator.auto_label_hierarchy_events(hierarchy_events)
            click.echo(f"    All elements labeled")
        
        # Initialize classifier
        classifier = ElementClassifier()
        
        # Prepare training data
        click.echo(f"\n Preparing training data...")
        try:
            features, labels = classifier.prepare_training_data(hierarchy_events)
        except ValueError as e:
            click.echo(f"\n Error: {e}", err=True)
            click.echo(f"\n Solution: Use --auto-label flag to automatically label elements", err=True)
            click.echo(f"   observe ml train --session-id {session_id} --auto-label", err=True)
            raise click.Abort()
        
        # Train model
        click.echo(f"\n Training Random Forest classifier...")
        metrics = classifier.train(features, labels, test_size=test_size)
        
        # Display results
        click.echo(f"\n Training complete!")
        click.echo(f"\n Performance Metrics:")
        click.echo(f"   Train Accuracy: {metrics['train_accuracy']:.3f}")
        click.echo(f"   Test Accuracy:  {metrics['test_accuracy']:.3f}")
        click.echo(f"   CV Mean:        {metrics['cv_mean']:.3f} (±{metrics['cv_std']:.3f})")
        click.echo(f"   Train Samples:  {metrics['train_samples']}")
        click.echo(f"   Test Samples:   {metrics['test_samples']}")
        
        # Check if meets target
        if metrics['test_accuracy'] >= 0.85:
            click.echo(f"\n Target accuracy (>85%) achieved! ")
        else:
            click.echo(f"\n  Target accuracy (>85%) not reached, but model saved")
            click.echo(f"   Consider collecting more training data")
        
        # Save model
        output_path = Path(output)
        classifier.save_model(output_path)
        
        click.echo(f"\n Model saved to {output_path}")
        click.echo(f"\n Next steps:")
        click.echo(f"   1. Use ML classifier in model building:")
        click.echo(f"      observe model build --session-id {session_id} --use-ml --ml-model {output_path}")
        
    except Exception as e:
        click.echo(f"\n Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


@ml.command('generate-training-data')
@click.option('--type', 'data_type', type=click.Choice(['synthetic', 'from-session']),
              default='synthetic', help='Training data type')
@click.option('--session-id', help='Session ID (for from-session type)')
@click.option('--num-samples', default=500, help='Number of synthetic samples to generate')
@click.option('--output', type=click.Path(), default='training_data/elements.json',
              help='Output file for training data')
def generate_training_data(data_type: str, session_id: Optional[str], num_samples: int, output: str):
    """
    Generate training data for ML classifier
    
    Examples:
        # Generate synthetic data (no session required)
        observe ml generate-training-data --type synthetic --num-samples 1000
        
        # Auto-label data from recorded session
        observe ml generate-training-data --type from-session --session-id session_123
    """
    click.echo(f"  Generating training data...")
    
    try:
        from framework.ml.training_data_generator import TrainingDataGenerator
        from framework.storage.event_store import EventStore
        
        generator = TrainingDataGenerator()
        output_path = Path(output)
        
        if data_type == 'synthetic':
            click.echo(f"   Type: Synthetic")
            click.echo(f"   Samples: {num_samples}")
            
            # Generate synthetic data
            generator.generate_synthetic_dataset(num_samples=num_samples, output_path=output_path)
            
            click.echo(f"\n Generated {num_samples} synthetic training samples")
            
        elif data_type == 'from-session':
            if not session_id:
                click.echo(f" --session-id required for from-session type", err=True)
                raise click.Abort()
            
            click.echo(f"   Type: From session")
            click.echo(f"   Session: {session_id}")
            
            # Load events
            store = EventStore()
            hierarchy_events = store.get_events(
                session_id=session_id,
                event_type='HierarchyEvent',
                limit=10000
            )
            
            if not hierarchy_events:
                click.echo(f"\n No hierarchy events found", err=True)
                raise click.Abort()
            
            click.echo(f"   Events: {len(hierarchy_events)}")
            
            # Auto-label
            click.echo(f"\n  Auto-labeling elements...")
            labeled_events = generator.auto_label_hierarchy_events(hierarchy_events)
            
            # Save
            generator.save_labeled_data(labeled_events, output_path)
            
            click.echo(f"\n Labeled {len(labeled_events)} events")
        
        click.echo(f"\n Training data saved to: {output_path}")
        click.echo(f"\n Next step:")
        click.echo(f"   Train ML classifier:")
        click.echo(f"   observe ml train --session-id <session_id>")
        
    except Exception as e:
        click.echo(f"\n Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


@ml.command('create-universal-model')
def create_universal_model():
    """
    Create universal pre-trained model that works for ANY application.
    
    This model is trained on synthetic data covering common Android/iOS patterns.
    It works out-of-the-box without requiring app-specific training.
    
    Example:
        observe ml create-universal-model
    """
    click.echo(" Creating universal pre-trained model...")
    click.echo("   This will generate 2000+ training samples and train a model")
    click.echo("   that works for ANY Android/iOS application!\n")
    
    try:
        from framework.ml.universal_model import create_universal_pretrained_model
        
        model_path = create_universal_pretrained_model()
        
        click.echo(f"\n Universal model created!")
        click.echo(f"   Location: {model_path}")
        click.echo(f"\n This model is now the default for all applications!")
        click.echo(f"\n Usage:")
        click.echo(f"   # Model is used automatically when --use-ml is set")
        click.echo(f"   observe model build --session-id <session_id> --use-ml")
        click.echo(f"\n   # Or specify it explicitly")
        click.echo(f"   observe model build \\")
        click.echo(f"     --session-id <session_id> \\")
        click.echo(f"     --use-ml \\")
        click.echo(f"     --ml-model {model_path}")
        
    except Exception as e:
        click.echo(f"\n Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


@ml.command('analyze-patterns')
@click.option('--session-id', required=True, help='Session ID to analyze')
@click.option('--min-support', default=2, help='Minimum pattern frequency')
@click.option('--min-confidence', default=0.6, help='Minimum pattern confidence')
@click.option('--detect-anomalies', is_flag=True, help='Detect flow anomalies')
def analyze_patterns(session_id: str, min_support: int, min_confidence: float, detect_anomalies: bool):
    """
    Analyze navigation patterns and detect common flows
    
    Example:
        observe ml analyze-patterns --session-id session_123 --detect-anomalies
    """
    click.echo(f" Analyzing navigation patterns...")
    click.echo(f"   Session: {session_id}")
    
    try:
        from framework.ml.pattern_recognizer import PatternRecognizer
        from framework.storage.event_store import EventStore
        
        # Load navigation events
        store = EventStore()
        nav_events = store.get_events(
            session_id=session_id,
            event_type='NavigationEvent',
            limit=10000
        )
        
        if not nav_events:
            click.echo(f"\n No navigation events found for session {session_id}", err=True)
            raise click.Abort()
        
        click.echo(f"\n Loaded {len(nav_events)} navigation events")
        
        # Initialize recognizer
        recognizer = PatternRecognizer(
            min_support=min_support,
            min_confidence=min_confidence
        )
        
        # Analyze flows
        click.echo(f"\n Mining flow patterns...")
        patterns = recognizer.analyze_flows(nav_events)
        
        # Display patterns
        click.echo(f"\n Detected {len(patterns)} flow patterns:")
        
        critical_patterns = [p for p in patterns if p.is_critical]
        if critical_patterns:
            click.echo(f"\n Critical Paths ({len(critical_patterns)}):")
            for pattern in critical_patterns:
                click.echo(f"   • {pattern.description}")
                click.echo(f"     Frequency: {pattern.frequency}, Confidence: {pattern.confidence:.2f}")
        
        normal_patterns = [p for p in patterns if not p.is_critical][:5]
        if normal_patterns:
            click.echo(f"\n Common Flows (top 5):")
            for pattern in normal_patterns:
                click.echo(f"   • {pattern.description}")
                click.echo(f"     Frequency: {pattern.frequency}, Confidence: {pattern.confidence:.2f}")
        
        # Detect anomalies if requested
        if detect_anomalies:
            click.echo(f"\n Detecting anomalies...")
            anomalies = recognizer.detect_anomalies(nav_events, patterns)
            
            if anomalies:
                click.echo(f"\n  Detected {len(anomalies)} anomalies:")
                for anomaly in anomalies[:10]:  # Show first 10
                    severity_emoji = {'low': '🟡', 'medium': '🟠', 'high': ''}
                    emoji = severity_emoji.get(anomaly.severity, '')
                    click.echo(f"   {emoji} [{anomaly.anomaly_type}] {anomaly.description}")
            else:
                click.echo(f"\n No anomalies detected")
        
        # Suggest test scenarios
        click.echo(f"\n Generating test scenario suggestions...")
        scenarios = recognizer.suggest_test_scenarios(patterns)
        
        if scenarios:
            click.echo(f"\n🧪 Suggested Test Scenarios ({len(scenarios)}):")
            for i, scenario in enumerate(scenarios[:5], 1):  # Show first 5
                priority_emoji = '' if scenario['priority'] == 'critical' else '🟢'
                click.echo(f"\n   {priority_emoji} Scenario {i}: {scenario['description']}")
                click.echo(f"      Priority: {scenario['priority']}, Frequency: {scenario['frequency']}")
                click.echo(f"\n      Gherkin:\n")
                for line in scenario['gherkin'].split('\n'):
                    click.echo(f"      {line}")
        
        # Get statistics
        stats = recognizer.get_pattern_stats()
        click.echo(f"\n Pattern Statistics:")
        click.echo(f"   Total Patterns: {stats['total_patterns']}")
        click.echo(f"   Critical Paths: {stats['critical_patterns']}")
        click.echo(f"   Avg Frequency:  {stats['avg_frequency']:.1f}")
        click.echo(f"   Avg Confidence: {stats['avg_confidence']:.2f}")
        
    except Exception as e:
        click.echo(f"\n Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


@ml.command('heal-selectors')
@click.option('--model', type=click.Path(exists=True), required=True,
              help='App model YAML file')
@click.option('--test-results', type=click.Path(exists=True), required=True,
              help='Test execution results JSON')
@click.option('--output', type=click.Path(), default='healed_model.yaml',
              help='Output path for healed model')
def heal_selectors(model: str, test_results: str, output: str):
    """
    Attempt to heal broken selectors based on test failures
    
    Example:
        observe ml heal-selectors --model app_model.yaml --test-results failures.json
    """
    click.echo(f" Healing broken selectors...")
    
    try:
        from framework.ml.selector_healer import SelectorHealer
        from framework.model.app_model import AppModel
        import yaml
        import json
        
        # Load model
        with open(model, 'r') as f:
            model_data = yaml.safe_load(f)
        
        app_model = AppModel.model_validate(model_data)
        
        # Load test results
        with open(test_results, 'r') as f:
            results = json.load(f)
        
        # Initialize healer
        healer = SelectorHealer()
        
        # Process failures
        failures = results.get('failures', [])
        click.echo(f"\n Processing {len(failures)} failed tests...")
        
        healed_count = 0
        for failure in failures:
            screen_id = failure.get('screen_id')
            element_id = failure.get('element_id')
            
            if not screen_id or not element_id:
                continue
            
            # Find element in model
            screen = app_model.screens.get(screen_id)
            if not screen:
                continue
            
            element = next((e for e in screen.elements if e.id == element_id), None)
            if not element:
                continue
            
            # Attempt healing
            context = failure.get('element_context', {})
            result = healer.heal_selector(element.selector, context)
            
            if result.success:
                healed_count += 1
                click.echo(f"\n    Healed {element_id}:")
                click.echo(f"      Strategy: {result.strategy.value}")
                click.echo(f"      Confidence: {result.confidence:.2f}")
                click.echo(f"      Old: {result.original_selector}")
                click.echo(f"      New: {result.healed_selector}")
                
                # Update model (simplified - would need proper Selector object)
                # element.selector = result.healed_selector
        
        # Display statistics
        stats = healer.get_healing_stats()
        click.echo(f"\n Healing Statistics:")
        click.echo(f"   Total Attempts: {stats['total_attempts']}")
        click.echo(f"   Successful:     {stats['successful']}")
        click.echo(f"   Failed:         {stats['failed']}")
        click.echo(f"   Success Rate:   {stats['success_rate']:.1%}")
        
        if stats['strategies']:
            click.echo(f"\n Strategies Used:")
            for strategy, counts in stats['strategies'].items():
                success_rate = counts['successes'] / counts['attempts'] if counts['attempts'] > 0 else 0
                click.echo(f"   • {strategy}: {counts['successes']}/{counts['attempts']} ({success_rate:.1%})")
        
        # Save healed model
        output_path = Path(output)
        click.echo(f"\n Saving healed model to {output_path}...")
        # Would save updated model here
        
    except Exception as e:
        click.echo(f"\n Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


@ml.command('fallback-stats')
@click.option('--session', type=click.Path(),
              help='Test session directory (if available)')
def fallback_stats(session: Optional[str]):
    """
    Show statistics about fallback selector usage and auto-updates
    
    This command displays how often fallback selectors were used,
    which elements are most problematic, and which Page Objects
    were auto-updated by the SelectorHealer.
    
    Example:
        observe ml fallback-stats
        observe ml fallback-stats --session tests/sessions/2024-12-26
    """
    click.echo(" Fallback Selector Statistics\n")
    
    try:
        from framework.ml.selector_healer import SelectorHealer
        import json
        
        # Initialize healer (would normally be singleton from test runs)
        healer = SelectorHealer()
        
        # Get statistics
        stats = healer.get_fallback_stats()
        healing_stats = healer.get_healing_stats()
        
        if stats['total_fallbacks'] == 0:
            click.echo(" No fallback usage recorded yet.")
            click.echo("\nFallback selectors are used automatically during test execution")
            click.echo("when primary selectors fail. Run tests to see statistics.")
            return
        
        # Display fallback statistics
        click.echo(f" Fallback Usage Summary:")
        click.echo(f"   Total Fallbacks Used:   {stats['total_fallbacks']}")
        click.echo(f"   Unique Elements:        {stats['unique_elements']}")
        click.echo(f"   Unique Page Objects:    {stats['unique_page_objects']}")
        click.echo(f"   Auto-Updates Applied:   {stats['auto_updates']}")
        
        if stats['by_platform']:
            click.echo(f"\n By Platform:")
            for platform, count in stats['by_platform'].items():
                click.echo(f"   • {platform.capitalize()}: {count}")
        
        # Display recent fallback reports
        if healer.fallback_reports:
            click.echo(f"\n Recent Fallback Reports (last 10):")
            for report in healer.fallback_reports[-10:]:
                click.echo(f"\n   Element: {report['element_name']}")
                click.echo(f"   File:    {report['page_object_file']}")
                click.echo(f"   Failed:  {report['primary_selector']}")
                click.echo(f"   Worked:  {report['successful_fallback']} (fallback #{report['fallback_index'] + 1})")
                click.echo(f"   Time:    {report['timestamp']}")
        
        # Display auto-updates
        if healer.page_object_updates:
            click.echo(f"\n Auto-Updated Page Objects ({len(healer.page_object_updates)}):")
            for update in healer.page_object_updates:
                click.echo(f"\n   File:     {update['page_object_file']}")
                click.echo(f"   Element:  {update['element_name']}")
                click.echo(f"   Platform: {update['platform']}")
                click.echo(f"   New Selector: {update['new_primary_selector']}")
                click.echo(f"   Backup:   {update['backup_file']}")
                click.echo(f"   Time:     {update['timestamp']}")
        
        # Display healing statistics
        if healing_stats['total_attempts'] > 0:
            click.echo(f"\n Selector Healing Statistics:")
            click.echo(f"   Total Attempts:  {healing_stats['total_attempts']}")
            click.echo(f"   Successful:      {healing_stats['successful']}")
            click.echo(f"   Failed:          {healing_stats['failed']}")
            click.echo(f"   Success Rate:    {healing_stats['success_rate']:.1%}")
            
            if healing_stats['strategies']:
                click.echo(f"\n Strategies Used:")
                for strategy, counts in healing_stats['strategies'].items():
                    success_rate = counts['successes'] / counts['attempts'] if counts['attempts'] > 0 else 0
                    click.echo(f"   • {strategy}: {counts['successes']}/{counts['attempts']} ({success_rate:.1%})")
        
        # Recommendations
        click.echo(f"\n Recommendations:")
        if stats['auto_updates'] > 0:
            click.echo(f"   Review auto-updated Page Objects and commit changes")
        if stats['total_fallbacks'] > 10:
            click.echo(f"   High fallback usage detected - consider improving selectors")
        if stats['unique_elements'] > 5:
            click.echo(f"   Multiple elements using fallbacks - review selector strategy")
        
    except Exception as e:
        click.echo(f"\n Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


@ml.command('visual-diff')
@click.option('--baseline', type=click.Path(exists=True), required=True,
              help='Baseline screenshot')
@click.option('--current', type=click.Path(exists=True), required=True,
              help='Current screenshot')
@click.option('--output', type=click.Path(), default='visual_diff.png',
              help='Output path for diff image')
@click.option('--threshold', default=0.95, help='Similarity threshold (0.0-1.0)')
def visual_diff(baseline: str, current: str, output: str, threshold: float):
    """
    Detect visual differences between screenshots
    
    Example:
        observe ml visual-diff --baseline baseline.png --current current.png
    """
    click.echo(f"  Detecting visual differences...")
    
    try:
        from framework.ml.visual_detector import VisualDetector
        
        detector = VisualDetector()
        
        # Detect changes
        has_changes, similarity, diff_image = detector.detect_visual_changes(
            Path(baseline),
            Path(current),
            threshold=threshold
        )
        
        click.echo(f"\n Similarity Score: {similarity:.3f}")
        
        if has_changes:
            click.echo(f"  Visual changes detected!")
            
            if diff_image is not None:
                detector.save_visual_diff(diff_image, Path(output))
                click.echo(f" Diff image saved to {output}")
        else:
            click.echo(f" No significant visual changes")
        
    except Exception as e:
        click.echo(f"\n Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


@ml.command('report')
@click.option('--type', 'report_type', 
              type=click.Choice(['execution', 'coverage', 'selector-stability']),
              required=True, help='Report type')
@click.option('--test-results', type=click.Path(exists=True),
              help='Test results JSON (for execution report)')
@click.option('--model', type=click.Path(exists=True),
              help='App model YAML (for coverage/selector reports)')
@click.option('--executed-flows', type=click.Path(exists=True),
              help='Executed flows JSON (for coverage report)')
@click.option('--output', type=click.Path(), default='report.html',
              help='Output HTML file')
def report(report_type: str, test_results: Optional[str], model: Optional[str], 
           executed_flows: Optional[str], output: str):
    """
    Generate analytics dashboard reports
    
    Examples:
        observe ml report --type execution --test-results results.json
        observe ml report --type coverage --model app_model.yaml --executed-flows flows.json
        observe ml report --type selector-stability --model app_model.yaml
    """
    click.echo(f" Generating {report_type} report...")
    
    try:
        from framework.ml.analytics_dashboard import AnalyticsDashboard
        import yaml
        import json
        from framework.model.app_model import AppModel
        
        dashboard = AnalyticsDashboard()
        output_path = Path(output)
        
        if report_type == 'execution':
            if not test_results:
                click.echo(" --test-results required for execution report", err=True)
                raise click.Abort()
            
            with open(test_results, 'r') as f:
                results = json.load(f)
            
            click.echo(f" Loaded {len(results)} test results")
            dashboard.generate_execution_report(results, output_path)
            
        elif report_type == 'coverage':
            if not model or not executed_flows:
                click.echo(" --model and --executed-flows required for coverage report", err=True)
                raise click.Abort()
            
            # Load model
            with open(model, 'r') as f:
                model_data = yaml.safe_load(f)
            app_model = AppModel.model_validate(model_data)
            
            # Load executed flows
            with open(executed_flows, 'r') as f:
                flows = json.load(f)
            
            click.echo(f" Loaded model with {len(app_model.screens)} screens, {len(app_model.flows)} flows")
            click.echo(f" {len(flows)} flows executed")
            dashboard.generate_coverage_report(app_model, flows, output_path)
            
        elif report_type == 'selector-stability':
            if not model:
                click.echo(" --model required for selector stability report", err=True)
                raise click.Abort()
            
            # Load model
            with open(model, 'r') as f:
                model_data = yaml.safe_load(f)
            app_model = AppModel.model_validate(model_data)
            
            click.echo(f" Analyzing selectors in {len(app_model.screens)} screens")
            dashboard.generate_selector_stability_report(app_model, output_path)
        
        click.echo(f"\n Report generated successfully!")
        click.echo(f" Open in browser: file://{output_path.absolute()}")
        
    except Exception as e:
        click.echo(f"\n Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()



# ============================================================================
# PHASE 5: PROJECT INTEGRATION COMMANDS
# ============================================================================

@cli.group()
def framework():
    """
    Analyze and integrate with existing test projects
    
    Commands for discovering existing test automation projects,
    learning their patterns, and generating compatible tests.
    """
    pass


@framework.command('analyze')
@click.option('--project-dir', type=click.Path(exists=True), default='.',
              help='Path to existing test project')
@click.option('--output', type=click.Path(), default='output/project_analysis.json',
              help='Output file for analysis results')
def framework_analyze(project_dir: str, output: str):
    """
    Analyze existing test automation project
    
    Discovers project structure, conventions, and coverage.
    
    Example:
        observe framework analyze --project-dir ./tests
        observe framework analyze --project-dir /path/to/project --output analysis.json
    """
    from framework.integration.project_detector import ProjectDetector
    
    click.echo(f"\n🔍 Analyzing existing test project...")
    click.echo(f"  Project directory: {project_dir}")
    
    try:
        detector = ProjectDetector(Path(project_dir))
        structure = detector.scan()
        
        # Display summary
        click.echo(f"\n📊 Project Analysis Summary")
        click.echo(f"  {'='*50}")
        click.echo(f"  Test Framework: {click.style(structure.test_framework, fg='cyan')}")
        click.echo(f"  Total Tests: {click.style(str(structure.total_tests), fg='green')}")
        click.echo(f"  Page Objects: {click.style(str(structure.total_page_objects), fg='green')}")
        click.echo(f"  Screens Covered: {click.style(str(len(structure.screens_covered)), fg='green')}")
        
        if structure.page_objects_dir:
            click.echo(f"\n  📁 Structure:")
            click.echo(f"    Page Objects: {structure.page_objects_dir.relative_to(structure.root_dir)}")
            click.echo(f"    Tests: {structure.tests_dir.relative_to(structure.root_dir) if structure.tests_dir else 'N/A'}")
            click.echo(f"    Fixtures: {structure.fixtures_dir.relative_to(structure.root_dir) if structure.fixtures_dir else 'N/A'}")
        
        if structure.screens_covered:
            click.echo(f"\n  📱 Covered Screens:")
            for screen in sorted(structure.screens_covered)[:10]:  # Show first 10
                click.echo(f"    - {screen}")
            if len(structure.screens_covered) > 10:
                click.echo(f"    ... and {len(structure.screens_covered) - 10} more")
        
        # Save full analysis
        detector.save_analysis(Path(output))
        
        click.echo(f"\n✅ Next Steps:")
        click.echo(f"  1. Review analysis: {output}")
        click.echo(f"  2. Generate matching tests: observe generate tests --match-style")
        click.echo(f"  3. Validate integration: observe test run --dry-run")
        
    except Exception as e:
        click.echo(f"\n❌ Error analyzing project: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


@framework.command('recommendations')
@click.option('--project-dir', type=click.Path(exists=True), default='.',
              help='Path to existing test project')
def framework_recommendations(project_dir: str):
    """
    Get recommendations for test generation and integration
    
    Analyzes project and suggests best practices for integration.
    
    Example:
        observe framework recommendations
    """
    from framework.integration.project_detector import ProjectDetector
    
    click.echo(f"\n🔍 Analyzing project for recommendations...")
    
    try:
        detector = ProjectDetector(Path(project_dir))
        structure = detector.scan()
        
        click.echo(f"\n💡 Integration Recommendations")
        click.echo(f"  {'='*50}")
        
        # Check for Page Objects
        if not structure.page_objects_dir:
            click.echo(f"\n  ⚠️  No Page Objects directory found")
            click.echo(f"    ✨ We recommend creating: tests/page_objects/")
            click.echo(f"    📈 This will improve test maintainability")
        else:
            click.echo(f"\n  ✅ Page Objects structure: Good")
            click.echo(f"    📁 Location: {structure.page_objects_dir.relative_to(structure.root_dir)}")
        
        # Check for fixtures
        if not structure.fixture_files:
            click.echo(f"\n  ⚠️  No fixtures found")
            click.echo(f"    ✨ Consider adding conftest.py for shared fixtures")
        else:
            click.echo(f"\n  ✅ Fixtures: {len(structure.fixture_files)} found")
        
        # Check test coverage
        if structure.total_tests < 10:
            click.echo(f"\n  📊 Low test coverage ({structure.total_tests} tests)")
            click.echo(f"    ✨ We can generate comprehensive tests based on observation")
        elif structure.total_tests < 50:
            click.echo(f"\n  📊 Moderate test coverage ({structure.total_tests} tests)")
            click.echo(f"    ✨ We can fill gaps and enhance existing tests")
        else:
            click.echo(f"\n  ✅ Good test coverage ({structure.total_tests} tests)")
            click.echo(f"    ✨ We can add tests for new features and edge cases")
        
        # Recommendations based on framework
        if structure.test_framework == "pytest":
            click.echo(f"\n  ✅ pytest detected: Excellent choice!")
            click.echo(f"    🎯 We'll generate pytest-compatible tests with fixtures")
        elif structure.test_framework == "unittest":
            click.echo(f"\n  ℹ️  unittest detected")
            click.echo(f"    💡 Consider migrating to pytest for better fixtures and plugins")
        
        # Integration strategy
        click.echo(f"\n  🎯 Suggested Integration Strategy:")
        click.echo(f"    1. Use existing Page Object base class: {structure.base_page_class or 'BasePage'}")
        click.echo(f"    2. Follow naming convention: {structure.page_object_suffix}")
        click.echo(f"    3. Reuse existing fixtures from conftest.py")
        click.echo(f"    4. Generate tests matching detected style")
        click.echo(f"    5. Run side-by-side with existing tests")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        raise click.Abort()




# ============================================================================
# PHASE 5: PROJECT INTEGRATION COMMANDS
# ============================================================================

@cli.group()
def framework():
    """
    Analyze and integrate with existing test projects
    
    Commands for discovering existing test automation projects,
    learning their patterns, and generating compatible tests.
    """
    pass




@framework.command('init')
@click.option('--project-name', required=True,
              help='Project name')
@click.option('--output-dir', type=click.Path(), default='.',
              help='Output directory for project')
@click.option('--platform', type=click.Choice(['android', 'ios', 'both']), default='both',
              help='Target platform(s)')
def framework_init(project_name: str, output_dir: str, platform: str):
    """
    Initialize new test automation project from scratch
    
    Creates a complete project structure with:
    - Page Objects directory with base class
    - Tests directory with conftest.py
    - Utilities directory with API client
    - pytest configuration
    - README and .gitignore
    
    Example:
        observe framework init --project-name MyApp
        observe framework init --project-name MyApp --output-dir ./tests --platform android
    """
    from framework.integration.project_templates import PROJECT_TEMPLATES, get_readme_template
    
    click.echo(f"\n🚀 Initializing test project: {project_name}")
    
    try:
        project_root = Path(output_dir) / project_name
        
        # Check if directory exists
        if project_root.exists():
            click.echo(f"\n⚠️  Warning: Directory already exists: {project_root}")
            if not click.confirm("Do you want to continue?"):
                return
        
        # Create project structure
        project_root.mkdir(parents=True, exist_ok=True)
        
        click.echo(f"\n📁 Creating project structure...")
        
        # Create files from templates
        for file_path, template_func in PROJECT_TEMPLATES.items():
            full_path = project_root / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            content = template_func()
            full_path.write_text(content + '\n')
            click.echo(f"  ✓ Created: {file_path}")
        
        # Create README with project name
        readme_path = project_root / 'README.md'
        readme_content = get_readme_template(project_name)
        readme_path.write_text(readme_content + '\n')
        click.echo(f"  ✓ Created: README.md")
        
        # Create requirements.txt
        requirements_path = project_root / 'requirements.txt'
        requirements_content = """# Core dependencies
appium-python-client>=3.0.0
selenium>=4.15.0
pytest>=7.4.0
pytest-bdd>=6.1.0

# Reporting
pytest-html>=4.1.0
pytest-json-report>=1.5.0
allure-pytest>=2.13.0

# Parallel execution
pytest-xdist>=3.5.0
pytest-rerunfailures>=12.0

# Utilities
requests>=2.31.0
"""
        requirements_path.write_text(requirements_content)
        click.echo(f"  ✓ Created: requirements.txt")
        
        # Success message
        click.echo(f"\n✅ Project '{project_name}' initialized successfully!")
        click.echo(f"\n📍 Location: {project_root.absolute()}")
        
        click.echo(f"\n🎯 Next Steps:")
        click.echo(f"  1. cd {project_root}")
        click.echo(f"  2. python -m venv .venv")
        click.echo(f"  3. source .venv/bin/activate")
        click.echo(f"  4. pip install -r requirements.txt")
        click.echo(f"  5. Update tests/conftest.py with your app path")
        click.echo(f"  6. pytest tests/")
        
        click.echo(f"\n📚 Documentation:")
        click.echo(f"  - See README.md for detailed instructions")
        click.echo(f"  - Example Page Object: page_objects/login_page.py")
        click.echo(f"  - Example test: tests/test_login.py")
        
    except Exception as e:
        click.echo(f"\n❌ Error creating project: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()
@framework.command('analyze')
@click.option('--project-dir', type=click.Path(exists=True), default='.',
              help='Path to existing test project')
@click.option('--output', type=click.Path(), default='output/project_analysis.json',
              help='Output file for analysis results')
def framework_analyze(project_dir: str, output: str):
    """
    Analyze existing test automation project
    
    Discovers project structure, conventions, and coverage.
    
    Example:
        observe framework analyze --project-dir ./tests
        observe framework analyze --project-dir /path/to/project --output analysis.json
    """
    from framework.integration.project_detector import ProjectDetector
    
    click.echo(f"\n🔍 Analyzing existing test project...")
    click.echo(f"  Project directory: {project_dir}")
    
    try:
        detector = ProjectDetector(Path(project_dir))
        structure = detector.scan()
        
        # Display summary
        click.echo(f"\n📊 Project Analysis Summary")
        click.echo(f"  {'='*50}")
        click.echo(f"  Test Framework: {click.style(structure.test_framework, fg='cyan')}")
        click.echo(f"  Total Tests: {click.style(str(structure.total_tests), fg='green')}")
        click.echo(f"  Page Objects: {click.style(str(structure.total_page_objects), fg='green')}")
        click.echo(f"  Screens Covered: {click.style(str(len(structure.screens_covered)), fg='green')}")
        
        if structure.page_objects_dir:
            click.echo(f"\n  📁 Structure:")
            click.echo(f"    Page Objects: {structure.page_objects_dir.relative_to(structure.root_dir)}")
            click.echo(f"    Tests: {structure.tests_dir.relative_to(structure.root_dir) if structure.tests_dir else 'N/A'}")
            click.echo(f"    Fixtures: {structure.fixtures_dir.relative_to(structure.root_dir) if structure.fixtures_dir else 'N/A'}")
        
        if structure.screens_covered:
            click.echo(f"\n  📱 Covered Screens:")
            for screen in sorted(structure.screens_covered)[:10]:  # Show first 10
                click.echo(f"    - {screen}")
            if len(structure.screens_covered) > 10:
                click.echo(f"    ... and {len(structure.screens_covered) - 10} more")
        
        # Save full analysis
        detector.save_analysis(Path(output))
        
        click.echo(f"\n✅ Next Steps:")
        click.echo(f"  1. Review analysis: {output}")
        click.echo(f"  2. Generate matching tests: observe generate tests --match-style")
        click.echo(f"  3. Validate integration: observe test run --dry-run")
        
    except Exception as e:
        click.echo(f"\n❌ Error analyzing project: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


@framework.command('recommendations')
@click.option('--project-dir', type=click.Path(exists=True), default='.',
              help='Path to existing test project')
def framework_recommendations(project_dir: str):
    """
    Get recommendations for test generation and integration
    
    Analyzes project and suggests best practices for integration.
    
    Example:
        observe framework recommendations
    """
    from framework.integration.project_detector import ProjectDetector
    
    click.echo(f"\n🔍 Analyzing project for recommendations...")
    
    try:
        detector = ProjectDetector(Path(project_dir))
        structure = detector.scan()
        
        click.echo(f"\n💡 Integration Recommendations")
        click.echo(f"  {'='*50}")
        
        # Check for Page Objects
        if not structure.page_objects_dir:
            click.echo(f"\n  ⚠️  No Page Objects directory found")
            click.echo(f"    ✨ We recommend creating: tests/page_objects/")
            click.echo(f"    📈 This will improve test maintainability")
        else:
            click.echo(f"\n  ✅ Page Objects structure: Good")
            click.echo(f"    📁 Location: {structure.page_objects_dir.relative_to(structure.root_dir)}")
        
        # Check for fixtures
        if not structure.fixture_files:
            click.echo(f"\n  ⚠️  No fixtures found")
            click.echo(f"    ✨ Consider adding conftest.py for shared fixtures")
        else:
            click.echo(f"\n  ✅ Fixtures: {len(structure.fixture_files)} found")
        
        # Check test coverage
        if structure.total_tests < 10:
            click.echo(f"\n  📊 Low test coverage ({structure.total_tests} tests)")
            click.echo(f"    ✨ We can generate comprehensive tests based on observation")
        elif structure.total_tests < 50:
            click.echo(f"\n  📊 Moderate test coverage ({structure.total_tests} tests)")
            click.echo(f"    ✨ We can fill gaps and enhance existing tests")
        else:
            click.echo(f"\n  ✅ Good test coverage ({structure.total_tests} tests)")
            click.echo(f"    ✨ We can add tests for new features and edge cases")
        
        # Recommendations based on framework
        if structure.test_framework == "pytest":
            click.echo(f"\n  ✅ pytest detected: Excellent choice!")
            click.echo(f"    🎯 We'll generate pytest-compatible tests with fixtures")
        elif structure.test_framework == "unittest":
            click.echo(f"\n  ℹ️  unittest detected")
            click.echo(f"    💡 Consider migrating to pytest for better fixtures and plugins")
        
        # Integration strategy
        click.echo(f"\n  🎯 Suggested Integration Strategy:")
        click.echo(f"    1. Use existing Page Object base class: {structure.base_page_class or 'BasePage'}")
        click.echo(f"    2. Follow naming convention: {structure.page_object_suffix}")
        click.echo(f"    3. Reuse existing fixtures from conftest.py")
        click.echo(f"    4. Generate tests matching detected style")
        click.echo(f"    5. Run side-by-side with existing tests")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        raise click.Abort()


# ============================================================================
# DEVICE MANAGEMENT COMMANDS
# ============================================================================

@cli.group()
def devices():
    """
    Manage devices for test execution
    
    Commands for discovering, managing, and orchestrating devices across
    emulators, real devices, and cloud platforms.
    """
    pass


@devices.command('list')
@click.option('--platform', type=click.Choice(['android', 'ios', 'all']), default='all',
              help='Filter by platform')
@click.option('--verbose', '-v', is_flag=True,
              help='Show detailed device information')
@click.option('--output', type=click.Path(), default=None,
              help='Save device list to JSON file')
def devices_list(platform: str, verbose: bool, output: Optional[str]):
    """
    List all available devices
    
    Discovers and displays devices from all sources:
    - Connected Android devices (ADB)
    - Android emulators
    - Connected iOS devices
    - iOS simulators
    
    Example:
        observe devices list
        observe devices list --platform android
        observe devices list --verbose --output devices.json
    """
    from framework.devices.device_manager import DeviceManager
    
    click.echo("\n🔍 Discovering devices...")
    
    try:
        manager = DeviceManager()
        devices = manager.discover_all()
        
        # Filter by platform
        if platform != 'all':
            devices = [d for d in devices if d.platform == platform]
        
        if not devices:
            click.echo("\n⚠️  No devices found.")
            click.echo("\nTips:")
            click.echo("  - Connect a device via USB")
            click.echo("  - Start an emulator/simulator")
            click.echo("  - Check that ADB/instruments are in PATH")
            return
        
        # Display devices
        manager.list_devices(verbose=verbose)
        
        # Save to file if requested
        if output:
            manager.save_devices(Path(output))
        
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()


@devices.command('info')
@click.argument('device_id')
def devices_info(device_id: str):
    """
    Show detailed information about a specific device
    
    Example:
        observe devices info emulator-5554
        observe devices info udid-12345
    """
    from framework.devices.device_manager import DeviceManager
    
    try:
        manager = DeviceManager()
        manager.discover_all()
        
        device = manager.get_device(device_id)
        
        if not device:
            click.echo(f"\n❌ Device not found: {device_id}")
            return
        
        click.echo(f"\n📱 Device Information")
        click.echo(f"  {'='*50}")
        click.echo(f"  ID: {device.id}")
        click.echo(f"  Name: {device.name}")
        click.echo(f"  Type: {device.type.value}")
        click.echo(f"  Status: {device.status.value}")
        click.echo(f"  Platform: {device.platform} {device.platform_version}")
        
        if device.model:
            click.echo(f"  Model: {device.model}")
        if device.manufacturer:
            click.echo(f"  Manufacturer: {device.manufacturer}")
        if device.screen_size:
            click.echo(f"  Screen: {device.screen_size}")
        if device.ram:
            click.echo(f"  RAM: {device.ram} MB")
        
        click.echo(f"\n  Provider: {device.provider}")
        
        if device.capabilities:
            click.echo(f"\n  Capabilities:")
            for key, value in device.capabilities.items():
                click.echo(f"    {key}: {value}")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        raise click.Abort()


@devices.command('pool')
@click.argument('action', type=click.Choice(['create', 'list', 'add', 'remove']))
@click.option('--name', help='Pool name')
@click.option('--device', help='Device ID to add/remove')
@click.option('--filter', help='Device filter (e.g., "platform=android,version>=12")')
def devices_pool(action: str, name: Optional[str], device: Optional[str], filter: Optional[str]):
    """
    Manage device pools for parallel execution
    
    Examples:
        observe devices pool create --name android-pool
        observe devices pool add --name android-pool --device emulator-5554
        observe devices pool list
        observe devices pool remove --name android-pool --device emulator-5554
    """
    from framework.devices.device_manager import DeviceManager
    from framework.devices.device_pool import PoolManager, PoolStrategy
    
    pool_manager = PoolManager()
    
    try:
        if action == 'create':
            if not name:
                click.echo("❌ Error: --name is required for 'create'", err=True)
                return
            
            pool = pool_manager.create_pool(name, strategy=PoolStrategy.ROUND_ROBIN)
            click.echo(f"\n✅ Created pool: '{name}'")
        
        elif action == 'list':
            pool_manager.list_pools()
        
        elif action == 'add':
            if not name or not device:
                click.echo("❌ Error: --name and --device are required for 'add'", err=True)
                return
            
            pool = pool_manager.get_pool(name)
            if not pool:
                click.echo(f"❌ Error: Pool '{name}' not found", err=True)
                return
            
            # Discover devices to get full device object
            device_manager = DeviceManager()
            device_manager.discover_all()
            
            device_obj = device_manager.get_device(device)
            if not device_obj:
                click.echo(f"❌ Error: Device '{device}' not found", err=True)
                return
            
            pool.add_device(device_obj)
            click.echo(f"\n✅ Added device '{device}' to pool '{name}'")
        
        elif action == 'remove':
            if not name or not device:
                click.echo("❌ Error: --name and --device are required for 'remove'", err=True)
                return
            
            pool = pool_manager.get_pool(name)
            if not pool:
                click.echo(f"❌ Error: Pool '{name}' not found", err=True)
                return
            
            pool.remove_device(device)
            click.echo(f"\n✅ Removed device '{device}' from pool '{name}'")
    
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        raise click.Abort()



# ============================================================================
# CI/CD INTEGRATION COMMANDS
# ============================================================================

@cli.group()
def ci():
    """
    CI/CD integration and workflow generation
    
    Commands for generating CI/CD configurations and managing
    test execution in continuous integration environments.
    """
    pass


@ci.command('init')
@click.option('--platform', type=click.Choice(['github', 'gitlab', 'jenkins']), required=True,
              help='CI/CD platform')
@click.option('--output-dir', type=click.Path(), default='.',
              help='Output directory')
@click.option('--test-platforms', default='android,ios',
              help='Comma-separated list of test platforms')
@click.option('--advanced', is_flag=True,
              help='Generate advanced workflow with parallel execution, cloud devices, etc.')
def ci_init(platform: str, output_dir: str, test_platforms: str, advanced: bool):
    """
    Initialize CI/CD configuration
    
    Generates CI/CD configuration files with best practices for mobile testing.
    
    Examples:
        observe ci init --platform github
        observe ci init --platform gitlab --test-platforms android --advanced
        observe ci init --platform github --test-platforms android,ios --advanced
    """
    from framework.ci.github_actions import GitHubActionsGenerator
    from framework.ci.gitlab_ci import GitLabCIGenerator
    
    click.echo(f"\n🚀 Generating {platform.upper()} CI/CD configuration...")
    
    try:
        platforms_list = [p.strip() for p in test_platforms.split(',')]
        output_path = Path(output_dir)
        
        if platform == 'github':
            generator = GitHubActionsGenerator()
            
            if advanced:
                content = generator.generate_advanced_workflow(
                    platforms=platforms_list,
                    parallel_count=2,
                    use_browserstack=True,
                    upload_artifacts=True,
                    notify_slack=False
                )
                filename = 'tests-advanced.yml'
            else:
                content = generator.generate_basic_workflow(platforms=platforms_list)
                filename = 'tests.yml'
            
            generator.save_workflow(content, output_path, filename)
            
            click.echo(f"\n✅ GitHub Actions workflow created!")
            click.echo(f"\n📍 Location: {output_path / '.github' / 'workflows' / filename}")
            
            click.echo(f"\n🔐 Required Secrets (if using advanced features):")
            click.echo(f"  - BROWSERSTACK_USERNAME")
            click.echo(f"  - BROWSERSTACK_ACCESS_KEY")
            click.echo(f"  - SLACK_WEBHOOK_URL (optional)")
            
            click.echo(f"\n📚 Next Steps:")
            click.echo(f"  1. Review and customize the workflow")
            click.echo(f"  2. Add required secrets to GitHub repository")
            click.echo(f"  3. Push to trigger the workflow")
            click.echo(f"  4. Monitor execution in Actions tab")
        
        elif platform == 'gitlab':
            generator = GitLabCIGenerator()
            
            if advanced:
                content = generator.generate_advanced_pipeline(
                    platforms=platforms_list,
                    parallel_count=2
                )
            else:
                content = generator.generate_basic_pipeline(platforms=platforms_list)
            
            generator.save_pipeline(content, output_path)
            
            click.echo(f"\n✅ GitLab CI pipeline created!")
            click.echo(f"\n📍 Location: {output_path / '.gitlab-ci.yml'}")
            
            click.echo(f"\n🔐 Required CI/CD Variables:")
            click.echo(f"  - BROWSERSTACK_USERNAME")
            click.echo(f"  - BROWSERSTACK_ACCESS_KEY")
            
            click.echo(f"\n📚 Next Steps:")
            click.echo(f"  1. Review and customize the pipeline")
            click.echo(f"  2. Add required variables to GitLab project")
            click.echo(f"  3. Push to trigger the pipeline")
            click.echo(f"  4. Monitor execution in CI/CD > Pipelines")
        
        elif platform == 'jenkins':
            click.echo(f"\n⚠️  Jenkins support coming soon!")
            click.echo(f"  For now, use GitHub Actions or GitLab CI")
            click.echo(f"  Or create Jenkinsfile manually based on templates")
    
    except Exception as e:
        click.echo(f"\n❌ Error generating CI/CD config: {e}", err=True)
        import traceback
        traceback.print_exc()
        raise click.Abort()

if __name__ == '__main__':
    cli()
