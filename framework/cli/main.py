"""
Main CLI entry point for Mobile Test Recorder

Simplified main module that imports command groups from separate modules.
"""

import click
from framework import __version__

# Import command groups
from framework.cli.business_logic_commands import business_logic
from framework.cli.project_commands import project
from framework.cli.record_commands import record
from framework.cli.generate_commands import generate
from framework.cli.rich_output import print_banner


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx):
    """
    📱 Mobile Test Recorder

    Intelligent Mobile Testing Platform - Observe, Analyze, Automate
    """
    ctx.ensure_object(dict)


# Register command groups
cli.add_command(business_logic)
cli.add_command(project)
cli.add_command(record)
cli.add_command(generate)


@cli.command()
def info():
    """Show framework information"""
    print_banner()
    click.echo("\n📦 Framework Information")
    click.echo(f"   Version: {__version__}")
    click.echo("   Platform: Mobile (Android & iOS)")
    click.echo("\n✨ Features:")
    click.echo("   • Business Logic Analysis")
    click.echo("   • Project Integration")
    click.echo("   • Session Recording")
    click.echo("   • Test Generation")
    click.echo("   • Rich CLI Interface")
    click.echo("\n📚 Documentation: See README.md")
    click.echo("🐛 Issues: https://github.com/VadimToptunov/mobile_test_recorder/issues")


if __name__ == "__main__":
    cli()
