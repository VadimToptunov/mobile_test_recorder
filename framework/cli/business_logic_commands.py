"""
CLI commands for business logic analysis
"""

import click
from pathlib import Path
import json
import yaml


@click.group()
def business():
    """
    Business logic analysis commands
    
    Extract and analyze business logic from source code
    """
    pass


@business.command()
@click.option('--source', type=click.Path(exists=True), required=True,
              help='Path to source code')
@click.option('--output', type=click.Path(), default='business_logic.yaml',
              help='Output file for analysis results')
@click.option('--format', type=click.Choice(['yaml', 'json']), default='yaml',
              help='Output format')
def analyze(source: str, output: str, format: str):
    """
    Analyze business logic from source code
    
    Example:
        observe business analyze --source ./app/src --output business_logic.yaml
    """
    from framework.analyzers.business_logic_analyzer import BusinessLogicAnalyzer
    
    click.echo(f"\n🔍 Analyzing business logic...")
    click.echo(f"   Source: {source}")
    
    analyzer = BusinessLogicAnalyzer(Path(source))
    analysis = analyzer.analyze()
    
    # Print summary
    click.echo(f"\n📊 Analysis Summary:")
    click.echo(f"   User Flows: {len(analysis.user_flows)}")
    click.echo(f"   Business Rules: {len(analysis.business_rules)}")
    click.echo(f"   Data Models: {len(analysis.data_models)}")
    click.echo(f"   Mock Data Entities: {len(analysis.mock_data)}")
    
    # Show user flows
    if analysis.user_flows:
        click.echo(f"\n👤 User Flows:")
        for flow in analysis.user_flows:
            click.echo(f"   • {flow.name}")
            click.echo(f"     Steps: {len(flow.steps)}")
            click.echo(f"     Entry: {flow.entry_point}")
    
    # Show data models
    if analysis.data_models:
        click.echo(f"\n📦 Data Models:")
        for model in analysis.data_models:
            click.echo(f"   • {model.name} ({len(model.fields)} fields)")
    
    # Show mock data
    if analysis.mock_data:
        click.echo(f"\n🎭 Mock Test Data:")
        for entity, data in analysis.mock_data.items():
            if isinstance(data, dict) and 'count' in data:
                click.echo(f"   • {entity}: {data['count']} records (IDs {data['start_id']}-{data['end_id']})")
    
    # Save to file
    output_path = Path(output)
    export_data = analyzer.export_to_json()
    
    with open(output_path, 'w') as f:
        if format == 'json':
            json.dump(export_data, f, indent=2)
        else:
            yaml.dump(export_data, f, default_flow_style=False, sort_keys=False)
    
    click.echo(f"\n💾 Analysis saved to: {output_path}")
    click.echo(f"\nNext steps:")
    click.echo(f"  1. Review business logic: cat {output_path}")
    click.echo(f"  2. Generate scenarios: observe business scenarios --input {output_path}")
    click.echo(f"  3. Generate BDD features: observe business features --input {output_path}")


@business.command()
@click.option('--input', 'input_file', type=click.Path(exists=True), required=True,
              help='Business logic analysis file')
@click.option('--output', type=click.Path(), default='test_scenarios.yaml',
              help='Output file for test scenarios')
def scenarios(input_file: str, output: str):
    """
    Generate test scenarios from business logic
    
    Example:
        observe business scenarios --input business_logic.yaml
    """
    from framework.analyzers.business_logic_analyzer import BusinessLogicAnalyzer
    
    click.echo(f"\n🎯 Generating test scenarios...")
    
    # Load analysis
    with open(input_file) as f:
        if input_file.endswith('.json'):
            data = json.load(f)
        else:
            data = yaml.safe_load(f)
    
    # Reconstruct analyzer (simplified)
    analyzer = BusinessLogicAnalyzer(Path('.'))
    
    # Load data into analysis
    from framework.analyzers.business_logic_analyzer import (
        UserFlow, BusinessRule, DataModel, BusinessLogicAnalysis,
        BusinessRuleType
    )
    
    analysis = BusinessLogicAnalysis()
    
    for flow_data in data.get('user_flows', []):
        flow = UserFlow(
            name=flow_data['name'],
            description=flow_data['description'],
            steps=flow_data['steps'],
            entry_point=flow_data['entry_point'],
            success_outcome=flow_data['success_outcome'],
            failure_outcomes=flow_data.get('failure_outcomes', []),
            source_files=flow_data.get('source_files', [])
        )
        analysis.user_flows.append(flow)
    
    analyzer.analysis = analysis
    
    # Generate scenarios
    scenarios_list = analyzer.generate_test_scenarios()
    
    click.echo(f"\n✨ Generated {len(scenarios_list)} test scenarios:")
    for scenario in scenarios_list:
        emoji = "✅" if scenario['type'] == 'positive' else "❌"
        click.echo(f"   {emoji} {scenario['name']} [{scenario['priority']}]")
    
    # Save
    output_path = Path(output)
    with open(output_path, 'w') as f:
        yaml.dump({'scenarios': scenarios_list}, f, default_flow_style=False)
    
    click.echo(f"\n💾 Scenarios saved to: {output_path}")


@business.command()
@click.option('--input', 'input_file', type=click.Path(exists=True), required=True,
              help='Business logic analysis file')
@click.option('--output', type=click.Path(), default='features/business_logic.feature',
              help='Output BDD feature file')
def features(input_file: str, output: str):
    """
    Generate BDD feature files from business logic
    
    Example:
        observe business features --input business_logic.yaml
    """
    from framework.analyzers.business_logic_analyzer import (
        BusinessLogicAnalyzer, UserFlow, BusinessLogicAnalysis
    )
    
    click.echo(f"\n📝 Generating BDD features...")
    
    # Load analysis
    with open(input_file) as f:
        if input_file.endswith('.json'):
            data = json.load(f)
        else:
            data = yaml.safe_load(f)
    
    # Reconstruct analyzer
    analyzer = BusinessLogicAnalyzer(Path('.'))
    analysis = BusinessLogicAnalysis()
    
    for flow_data in data.get('user_flows', []):
        flow = UserFlow(
            name=flow_data['name'],
            description=flow_data['description'],
            steps=flow_data['steps'],
            entry_point=flow_data['entry_point'],
            success_outcome=flow_data['success_outcome'],
            failure_outcomes=flow_data.get('failure_outcomes', []),
            source_files=flow_data.get('source_files', [])
        )
        analysis.user_flows.append(flow)
    
    analyzer.analysis = analysis
    
    # Generate feature content
    feature_content = analyzer.generate_bdd_features()
    
    # Save
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(feature_content)
    
    click.echo(f"\n✅ BDD features generated:")
    click.echo(f"   File: {output_path}")
    click.echo(f"   Flows: {len(analysis.user_flows)}")
    
    click.echo(f"\nPreview:")
    click.echo("   " + "\n   ".join(feature_content.split("\n")[:15]))
    if len(feature_content.split("\n")) > 15:
        click.echo("   ...")


@business.command()
@click.option('--input', 'input_file', type=click.Path(exists=True), required=True,
              help='Business logic analysis file')
def testdata(input_file: str):
    """
    Show available mock test data
    
    Example:
        observe business testdata --input business_logic.yaml
    """
    click.echo(f"\n🎭 Available Mock Test Data:")
    
    # Load analysis
    with open(input_file) as f:
        if input_file.endswith('.json'):
            data = json.load(f)
        else:
            data = yaml.safe_load(f)
    
    mock_data = data.get('mock_data', {})
    
    if not mock_data:
        click.echo("   No mock data found")
        return
    
    for entity, entity_data in mock_data.items():
        click.echo(f"\n   📦 {entity}")
        if isinstance(entity_data, dict):
            if 'count' in entity_data:
                click.echo(f"      Records: {entity_data['count']}")
                click.echo(f"      ID Range: {entity_data['start_id']} - {entity_data['end_id']}")
                click.echo(f"      Source: {entity_data.get('source', 'N/A')}")
                click.echo(f"\n      💡 Use in tests:")
                click.echo(f"         Valid IDs: {entity_data['start_id']}, {entity_data['start_id']+1}, ...")
                click.echo(f"         Invalid ID: {entity_data['end_id'] + 100}")

