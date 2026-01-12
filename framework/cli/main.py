"""
Main CLI entry point for Mobile Test Recorder

Simplified main module that imports command groups from separate modules.
"""

import click
from framework import __version__
from framework.ml.self_learning import ModelUpdater

# Import command groups
from framework.cli.business_logic_commands import business
from framework.cli.project_commands import project
from framework.cli.record_commands import record
from framework.cli.generate_commands import generate
from framework.cli.dashboard_commands import dashboard
from framework.cli.healing_commands import heal
from framework.cli.device_commands import devices
from framework.cli.ml_commands import ml
from framework.cli import ml_selflearn_commands
from framework.cli.security_commands import security
from framework.cli.perf_commands import perf
from framework.cli.selection_commands import select
from framework.cli.config_commands import config
from framework.cli.notify_commands import notify
from framework.cli.visual_commands import visual
from framework.cli.data_commands import data
from framework.cli.execute_commands import execute
from framework.cli.mock_commands import mock
from framework.cli.selector_commands import selector
from framework.cli.parallel_commands import parallel
from framework.cli.ci_commands import ci
from framework.cli.doctor_command import doctor
from framework.cli.report_commands import report
from framework.cli.observability_commands import observe_ as observability
from framework.cli.a11y_commands import a11y
from framework.cli.load_commands import load
from framework.cli.docs_commands import docs
from framework.cli.rich_output import print_banner


def _check_ml_updates() -> None:
    """Check for ML model updates on CLI startup (once per day)."""
    try:
        from pathlib import Path
        import datetime
        import json

        # Check if we should update (once per day)
        update_check_file = Path(".observe_ml_check")
        should_check = True

        if update_check_file.exists():
            try:
                with open(update_check_file, "r") as f:
                    last_check = json.load(f).get("last_check")
                    last_check_date = datetime.datetime.fromisoformat(last_check)

                    # Check if last check was today
                    if last_check_date.date() == datetime.datetime.now().date():
                        should_check = False
            except Exception:
                pass  # If error reading, just check anyway

        if should_check:
            updater = ModelUpdater()
            update = updater.check_for_updates()

            # Save check timestamp
            with open(update_check_file, "w") as f:
                json.dump({"last_check": datetime.datetime.now().isoformat()}, f)

            if update:
                click.echo(f"\n💡 New ML model available: v{update['version']}")
                click.echo("   Run: observe ml update-model")

    except Exception:
        pass  # Silently fail - don't interrupt user workflow


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx):
    """
    📱 Mobile Test Recorder

    Intelligent Mobile Testing Platform - Observe, Analyze, Automate
    """
    ctx.ensure_object(dict)

    # Check for ML model updates on startup (once per day)
    _check_ml_updates()


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
cli.add_command(execute)
cli.add_command(mock)
cli.add_command(selector)
cli.add_command(parallel)
cli.add_command(ci)
cli.add_command(doctor)
cli.add_command(report)
cli.add_command(observability, name="observe")
cli.add_command(a11y)
cli.add_command(load)
cli.add_command(docs)

# Add self-learning ML commands as subgroup
ml.add_command(ml_selflearn_commands.check_updates)
ml.add_command(ml_selflearn_commands.update_model)
ml.add_command(ml_selflearn_commands.stats)
ml.add_command(ml_selflearn_commands.contribute)
ml.add_command(ml_selflearn_commands.export_cache)
ml.add_command(ml_selflearn_commands.clear_cache)
ml.add_command(ml_selflearn_commands.correct)
ml.add_command(ml_selflearn_commands.info)


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
