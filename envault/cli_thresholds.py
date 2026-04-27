"""CLI commands for managing key thresholds."""
from __future__ import annotations

import click

from envault.thresholds import (
    check_threshold,
    get_threshold,
    list_thresholds,
    remove_threshold,
    set_threshold,
)


@click.group("thresholds")
def thresholds_group() -> None:
    """Manage numeric thresholds for vault keys."""


@thresholds_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.option("--min", "min_val", type=float, default=None, help="Minimum allowed value.")
@click.option("--max", "max_val", type=float, default=None, help="Maximum allowed value.")
def set_cmd(vault: str, key: str, min_val: float | None, max_val: float | None) -> None:
    """Set a min and/or max threshold for KEY in VAULT."""
    if min_val is None and max_val is None:
        click.echo("Error: at least one of --min or --max must be provided.", err=True)
        raise SystemExit(1)
    if min_val is not None:
        set_threshold(vault, key, "min", min_val)
    if max_val is not None:
        set_threshold(vault, key, "max", max_val)
    click.echo(f"Threshold set for '{key}'.")


@thresholds_group.command("get")
@click.argument("vault")
@click.argument("key")
def get_cmd(vault: str, key: str) -> None:
    """Show the threshold(s) for KEY."""
    entry = get_threshold(vault, key)
    if entry is None:
        click.echo(f"No threshold set for '{key}'.")
    else:
        if "min" in entry:
            click.echo(f"min: {entry['min']}")
        if "max" in entry:
            click.echo(f"max: {entry['max']}")


@thresholds_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str) -> None:
    """Remove the threshold for KEY."""
    remove_threshold(vault, key)
    click.echo(f"Threshold removed for '{key}'.")


@thresholds_group.command("list")
@click.argument("vault")
def list_cmd(vault: str) -> None:
    """List all thresholds in VAULT."""
    data = list_thresholds(vault)
    if not data:
        click.echo("No thresholds set.")
        return
    for key, entry in sorted(data.items()):
        parts = []
        if "min" in entry:
            parts.append(f"min={entry['min']}")
        if "max" in entry:
            parts.append(f"max={entry['max']}")
        click.echo(f"{key}: {', '.join(parts)}")


@thresholds_group.command("check")
@click.argument("vault")
@click.argument("key")
@click.argument("value", type=float)
def check_cmd(vault: str, key: str, value: float) -> None:
    """Check VALUE against the threshold for KEY."""
    violations = check_threshold(vault, key, value)
    if not violations:
        click.echo("OK: value is within threshold.")
    else:
        for msg in violations:
            click.echo(f"VIOLATION: {msg}", err=True)
        raise SystemExit(1)
