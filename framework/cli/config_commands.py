"""
Config Management CLI commands

Commands for managing framework configuration.
"""

import click
from pathlib import Path
import json
from typing import Dict, Any, Optional

from framework.cli.rich_output import print_header, print_info, print_success, print_error
from rich.console import Console
from rich.table import Table

console = Console()


CONFIG_FILE = Path.home() / '.observe' / 'config.json'
DEFAULT_CONFIG: Dict[str, Any] = {
    'appium_server': 'http://localhost:4723',
    'implicit_wait': 10,
    'screenshot_on_failure': True,
    'parallel_workers': 4,
    'device_pool_strategy': 'round-robin',
    'healing_confidence_threshold': 0.8,
    'healing_auto_commit': False,
    'dashboard_port': 8080,
    'dashboard_host': 'localhost',
    'notification_slack_webhook': '',
    'notification_teams_webhook': '',
    'visual_threshold': 0.95,
    'api_timeout': 30,
    'log_level': 'INFO',
    'report_format': 'html',
    'ml_model_path': './models/element_classifier.pkl',
}


def load_config() -> Dict[str, Any]:
    """Load configuration from file"""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        # Merge with defaults (in case new keys were added)
        merged = DEFAULT_CONFIG.copy()
        merged.update(config)
        return merged
    except Exception as e:
        print_error(f"Failed to load config: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print_error(f"Failed to save config: {e}")
        raise


@click.group(name='config')
def config() -> None:
    """⚙️  Configuration management commands"""
    pass


@config.command()
@click.argument('key')
@click.argument('value')
def set(key: str, value: str) -> None:
    """Set a configuration value"""
    print_header("Set Configuration")

    cfg = load_config()

    if key not in DEFAULT_CONFIG:
        print_error(f"Unknown configuration key: {key}")
        print_info("\nAvailable keys:")
        for k in sorted(DEFAULT_CONFIG.keys()):
            print_info(f"  • {k}")
        raise click.Abort()

    # Type conversion based on default value
    default_type = type(DEFAULT_CONFIG[key])
    try:
        if default_type == bool:
            typed_value: Any = value.lower() in ('true', '1', 'yes', 'on')
        elif default_type == int:
            typed_value = int(value)
        elif default_type == float:
            typed_value = float(value)
        else:
            typed_value = value

        cfg[key] = typed_value
        save_config(cfg)

        print_success(f"✅ Set {key} = {typed_value}")
        print_info(f"Config file: {CONFIG_FILE}")

    except ValueError as e:
        print_error(f"Invalid value for {key}: {e}")
        print_info(f"Expected type: {default_type.__name__}")
        raise click.Abort()


@config.command()
@click.argument('key')
def get(key: str) -> None:
    """Get a configuration value"""
    cfg = load_config()

    if key not in cfg:
        print_error(f"Unknown configuration key: {key}")
        raise click.Abort()

    value = cfg[key]
    print_info(f"{key} = {value}")


@config.command(name='list')
def list_config() -> None:
    """List all configuration values"""
    print_header("Configuration")

    cfg = load_config()

    # Group by category
    categories = {
        'Appium': ['appium_server', 'implicit_wait', 'screenshot_on_failure'],
        'Execution': ['parallel_workers', 'device_pool_strategy', 'api_timeout'],
        'Healing': ['healing_confidence_threshold', 'healing_auto_commit'],
        'Dashboard': ['dashboard_port', 'dashboard_host'],
        'Notifications': ['notification_slack_webhook', 'notification_teams_webhook'],
        'Visual Testing': ['visual_threshold'],
        'ML': ['ml_model_path'],
        'Reporting': ['report_format', 'log_level'],
    }

    for category, keys in categories.items():
        table = Table(title=category)
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="yellow")
        table.add_column("Type", style="green")

        for key in keys:
            if key in cfg:
                value = cfg[key]
                value_str = str(value) if value != '' else '(not set)'
                type_name = type(value).__name__
                table.add_row(key, value_str, type_name)

        console.print(table)
        print()

    print_info(f"Config file: {CONFIG_FILE}")


@config.command()
@click.confirmation_option(prompt='Reset all configuration to defaults?')
def reset() -> None:
    """Reset configuration to defaults"""
    print_header("Reset Configuration")

    save_config(DEFAULT_CONFIG.copy())
    print_success("✅ Configuration reset to defaults")
    print_info(f"Config file: {CONFIG_FILE}")


@config.command()
def path() -> None:
    """Show configuration file path"""
    print_info(f"Config file: {CONFIG_FILE}")
    if CONFIG_FILE.exists():
        print_success("✅ File exists")
        print_info(f"Size: {CONFIG_FILE.stat().st_size} bytes")
    else:
        print_info("⚠️  File does not exist (using defaults)")


@config.command()
def validate() -> None:
    """Validate configuration"""
    print_header("Validate Configuration")

    cfg = load_config()
    errors = []
    warnings = []

    # Validate values
    if cfg['parallel_workers'] < 1:
        errors.append("parallel_workers must be >= 1")

    if not (0 <= cfg['healing_confidence_threshold'] <= 1):
        errors.append("healing_confidence_threshold must be between 0 and 1")

    if not (0 <= cfg['visual_threshold'] <= 1):
        errors.append("visual_threshold must be between 0 and 1")

    if cfg['dashboard_port'] < 1024 or cfg['dashboard_port'] > 65535:
        warnings.append("dashboard_port should be between 1024 and 65535")

    if cfg['notification_slack_webhook'] == '' and cfg['notification_teams_webhook'] == '':
        warnings.append("No notification webhooks configured")

    # Display results
    if errors:
        print_error(f"❌ {len(errors)} validation error(s):")
        for error in errors:
            print_error(f"  • {error}")
        raise click.Abort()

    if warnings:
        print_info(f"⚠️  {len(warnings)} warning(s):")
        for warning in warnings:
            print_info(f"  • {warning}")

    if not errors and not warnings:
        print_success("✅ Configuration is valid")

    print_info(f"\nConfig file: {CONFIG_FILE}")


@config.command()
@click.option('--output', '-o', type=click.Path(), help='Export to file')
def export(output: Optional[str]) -> None:
    """Export configuration"""
    cfg = load_config()

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(cfg, f, indent=2)
        print_success(f"✅ Exported to: {output_path}")
    else:
        print(json.dumps(cfg, indent=2))


@config.command()
@click.argument('file', type=click.Path(exists=True))
def import_file(file: str) -> None:
    """Import configuration from file"""
    print_header("Import Configuration")

    try:
        with open(file, 'r') as f:
            imported_cfg = json.load(f)

        # Validate keys
        unknown_keys = set(imported_cfg.keys()) - set(DEFAULT_CONFIG.keys())
        if unknown_keys:
            print_error(f"Unknown keys in import: {', '.join(unknown_keys)}")
            raise click.Abort()

        # Merge with current config
        current_cfg = load_config()
        current_cfg.update(imported_cfg)
        save_config(current_cfg)

        print_success(f"✅ Imported {len(imported_cfg)} settings from {file}")
        print_info(f"Config file: {CONFIG_FILE}")

    except Exception as e:
        print_error(f"Failed to import config: {e}")
        raise click.Abort()


if __name__ == '__main__':
    config()
