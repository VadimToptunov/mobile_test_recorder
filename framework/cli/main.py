"""
Main CLI entry point for Mobile Test Recorder

Simplified main module that imports command groups from separate modules.
"""

import click
from framework import __version__

# Import command groups
from framework.cli.business_logic_commands import business
from framework.cli.project_commands import project
from framework.cli.record_commands import record
from framework.cli.generate_commands import generate
from framework.cli.dashboard_commands import dashboard
from framework.cli.healing_commands import heal
from framework.cli.device_commands import devices
from framework.cli.ml_commands import ml
from framework.cli.security_commands import security
from framework.cli.perf_commands import perf
from framework.cli.selection_commands import select
from framework.cli.config_commands import config
from framework.cli.notify_commands import notify
from framework.cli.visual_commands import visual
from framework.cli.data_commands import data
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
cli.add_command(business)
cli.add_command(project)
cli.add_command(record)
cli.add_command(generate)
cli.add_command(dashboard)
cli.add_command(heal)
cli.add_command(devices)
cli.add_command(ml)
cli.add_command(security)
cli.add_command(perf)
cli.add_command(select)
cli.add_command(config)
cli.add_command(notify)
cli.add_command(visual)
cli.add_command(data)


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
    click.echo("   • Self-Healing Tests")
    click.echo("   • Device Management")
    click.echo("   • Dashboard & Analytics")
    click.echo("   • Rich CLI Interface")
    click.echo("\n📚 Documentation: See README.md")
    click.echo("🐛 Issues: https://github.com/VadimToptunov/mobile_test_recorder/issues")


if __name__ == "__main__":
    cli()
