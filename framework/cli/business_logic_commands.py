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
    click.echo(f"   Platform: {analyzer.platform.upper()}")
    click.echo(f"   User Flows: {len(analysis.user_flows)}")
    click.echo(f"   Business Rules: {len(analysis.business_rules)}")
    click.echo(f"   Data Models: {len(analysis.data_models)}")
    click.echo(f"   State Machines: {len(analysis.state_machines)}")
    click.echo(f"   Edge Cases: {len(analysis.edge_cases)}")
    click.echo(f"   Negative Tests: {len(analysis.negative_test_cases)}")
    click.echo(f"   Mock Data Entities: {len(analysis.mock_data)}")
    
    # Show user flows
    if analysis.user_flows:
        click.echo(f"\n👤 User Flows:")
        for flow in analysis.user_flows[:5]:  # Show first 5
            click.echo(f"   • {flow.name}")
            click.echo(f"     Steps: {len(flow.steps)}")
            click.echo(f"     Entry: {flow.entry_point}")
        if len(analysis.user_flows) > 5:
            click.echo(f"   ... and {len(analysis.user_flows) - 5} more")
    
    # Show state machines
    if analysis.state_machines:
        click.echo(f"\n🔄 State Machines:")
        for sm in analysis.state_machines[:3]:
            click.echo(f"   • {sm.name}: {len(sm.states)} states")
        if len(analysis.state_machines) > 3:
            click.echo(f"   ... and {len(analysis.state_machines) - 3} more")
    
    # Show edge cases summary
    if analysis.edge_cases:
        click.echo(f"\n⚠️ Edge Cases:")
        edge_types = {}
        for ec in analysis.edge_cases:
            edge_types[ec.type] = edge_types.get(ec.type, 0) + 1
        for edge_type, count in edge_types.items():
            click.echo(f"   • {edge_type}: {count} detected")
    
    # Show data models
    if analysis.data_models:
        click.echo(f"\n📦 Data Models:")
        for model in analysis.data_models[:5]:
            click.echo(f"   • {model.name} ({len(model.fields)} fields)")
        if len(analysis.data_models) > 5:
            click.echo(f"   ... and {len(analysis.data_models) - 5} more")
    
    # Show mock data
    if analysis.mock_data:
        click.echo(f"\n🎭 Mock Test Data:")
        for entity, data in list(analysis.mock_data.items())[:5]:
            if isinstance(data, dict) and 'count' in data:
                click.echo(f"   • {entity}: {data['count']} records (IDs {data['start_id']}-{data['end_id']})")
            elif isinstance(data, dict) and 'type' in data:
                click.echo(f"   • {entity}: {data['count']} {data['type']} objects")
        if len(analysis.mock_data) > 5:
            click.echo(f"   ... and {len(analysis.mock_data) - 5} more")
    
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


@business.command()
@click.option('--input', 'input_file', type=click.Path(exists=True), required=True,
              help='Business logic analysis file')
def edgecases(input_file: str):
    """
    Show detected edge cases
    
    Example:
        observe business edgecases --input business_logic.yaml
    """
    click.echo(f"\n⚠️ Detected Edge Cases:")
    
    # Load analysis
    with open(input_file) as f:
        if input_file.endswith('.json'):
            data = json.load(f)
        else:
            data = yaml.safe_load(f)
    
    edge_cases = data.get('edge_cases', [])
    
    if not edge_cases:
        click.echo("   No edge cases detected")
        return
    
    # Group by type
    by_type = {}
    for ec in edge_cases:
        ec_type = ec['type']
        if ec_type not in by_type:
            by_type[ec_type] = []
        by_type[ec_type].append(ec)
    
    for ec_type, cases in by_type.items():
        click.echo(f"\n   🔍 {ec_type.upper()} ({len(cases)} cases):")
        for ec in cases[:5]:  # Show first 5 per type
            click.echo(f"      • {ec['description']}")
            click.echo(f"        Severity: {ec['severity']}")
            if ec.get('test_data'):
                click.echo(f"        Test values: {ec['test_data']}")
        if len(cases) > 5:
            click.echo(f"      ... and {len(cases) - 5} more")


@business.command()
@click.option('--input', 'input_file', type=click.Path(exists=True), required=True,
              help='Business logic analysis file')
def statemachines(input_file: str):
    """
    Show extracted state machines
    
    Example:
        observe business statemachines --input business_logic.yaml
    """
    click.echo(f"\n🔄 Extracted State Machines:")
    
    # Load analysis
    with open(input_file) as f:
        if input_file.endswith('.json'):
            data = json.load(f)
        else:
            data = yaml.safe_load(f)
    
    state_machines = data.get('state_machines', [])
    
    if not state_machines:
        click.echo("   No state machines detected")
        return
    
    for sm in state_machines:
        click.echo(f"\n   📊 {sm['name']}")
        click.echo(f"      States: {', '.join(sm['states'])}")
        click.echo(f"      Initial: {sm['initial_state']}")
        
        if sm.get('transitions'):
            click.echo(f"      Transitions:")
            for from_state, to_states in sm['transitions'].items():
                if to_states:
                    click.echo(f"        {from_state} → {', '.join(to_states)}")


@business.command()
@click.option('--input', 'input_file', type=click.Path(exists=True), required=True,
              help='Business logic analysis file')
@click.option('--output', type=click.Path(), default='negative_tests.yaml',
              help='Output file for negative test cases')
def negative(input_file: str, output: str):
    """
    Show generated negative test cases
    
    Example:
        observe business negative --input business_logic.yaml
    """
    click.echo(f"\n❌ Generated Negative Test Cases:")
    
    # Load analysis
    with open(input_file) as f:
        if input_file.endswith('.json'):
            data = json.load(f)
        else:
            data = yaml.safe_load(f)
    
    negative_tests = data.get('negative_test_cases', [])
    
    if not negative_tests:
        click.echo("   No negative test cases generated")
        return
    
    click.echo(f"\n   Total: {len(negative_tests)} test cases")
    
    # Group by priority
    by_priority = {}
    for test in negative_tests:
        priority = test.get('priority', 'medium')
        if priority not in by_priority:
            by_priority[priority] = []
        by_priority[priority].append(test)
    
    for priority in ['critical', 'high', 'medium', 'low']:
        if priority in by_priority:
            tests = by_priority[priority]
            click.echo(f"\n   🔴 {priority.upper()} Priority ({len(tests)} tests):")
            for test in tests[:5]:
                click.echo(f"      • {test['name']}")
                click.echo(f"        Outcome: {test['expected_outcome']}")
            if len(tests) > 5:
                click.echo(f"      ... and {len(tests) - 5} more")
    
    # Save to file
    output_path = Path(output)
    with open(output_path, 'w') as f:
        yaml.dump({'negative_test_cases': negative_tests}, f, default_flow_style=False)
    
    click.echo(f"\n💾 Negative tests saved to: {output_path}")


