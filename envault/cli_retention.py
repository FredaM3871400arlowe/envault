"""CLI commands for retention policy management."""
from __future__ import annotations

from pathlib import Path

import click

from envault.retention import (
    VALID_UNITS,
    get_retention,
    list_expired,
    remove_retention,
    set_retention,
)


@click.group("retention")
def retention_group() -> None:
    """Manage key retention policies."""


@retention_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("value", type=int)
@click.argument("unit", type=click.Choice(VALID_UNITS))
def set_cmd(vault: str, key: str, value: int, unit: str) -> None:
    """Set a retention policy: VALUE UNIT (e.g. 30 days)."""
    vault_path = Path(vault)
    try:
        expires_at = set_retention(vault_path, key, value, unit)
        click.echo(f"Retention set for '{key}': {value} {unit} (expires {expires_at.date()}).")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@retention_group.command("get")
@click.argument("vault")
@click.argument("key")
def get_cmd(vault: str, key: str) -> None:
    """Show the retention policy for KEY."""
    entry = get_retention(Path(vault), key)
    if entry is None:
        click.echo(f"No retention policy set for '{key}'.")
    else:
        click.echo(
            f"{key}: {entry['value']} {entry['unit']} "
            f"(expires {entry['expires_at'][:10]})"
        )


@retention_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str) -> None:
    """Remove the retention policy for KEY."""
    removed = remove_retention(Path(vault), key)
    if removed:
        click.echo(f"Retention policy removed for '{key}'.")
    else:
        click.echo(f"No retention policy found for '{key}'.", err=True)
        raise SystemExit(1)


@retention_group.command("list-expired")
@click.argument("vault")
def list_expired_cmd(vault: str) -> None:
    """List keys whose retention period has elapsed."""
    expired = list_expired(Path(vault))
    if not expired:
        click.echo("No expired keys found.")
    else:
        for key in expired:
            click.echo(key)
