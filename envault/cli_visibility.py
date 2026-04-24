"""CLI commands for managing key visibility levels."""

from __future__ import annotations

import click

from .visibility import (
    VALID_LEVELS,
    get_visibility,
    list_by_level,
    load_visibility,
    remove_visibility,
    set_visibility,
)


@click.group("visibility")
def visibility_group() -> None:
    """Manage visibility levels for vault keys."""


@visibility_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("level", type=click.Choice(sorted(VALID_LEVELS), case_sensitive=False))
def set_cmd(vault: str, key: str, level: str) -> None:
    """Set the visibility LEVEL for KEY in VAULT."""
    set_visibility(vault, key, level.lower())
    click.echo(f"Visibility for '{key}' set to '{level.lower()}'.")


@visibility_group.command("get")
@click.argument("vault")
@click.argument("key")
def get_cmd(vault: str, key: str) -> None:
    """Show the visibility level of KEY in VAULT."""
    level = get_visibility(vault, key)
    if level is None:
        click.echo(f"No visibility set for '{key}'.")
    else:
        click.echo(level)


@visibility_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str) -> None:
    """Remove the visibility entry for KEY in VAULT."""
    removed = remove_visibility(vault, key)
    if removed:
        click.echo(f"Visibility entry for '{key}' removed.")
    else:
        click.echo(f"No visibility entry found for '{key}'.")
        raise SystemExit(1)


@visibility_group.command("list")
@click.argument("vault")
@click.option("--level", type=click.Choice(sorted(VALID_LEVELS), case_sensitive=False), default=None)
def list_cmd(vault: str, level: str | None) -> None:
    """List visibility entries in VAULT, optionally filtered by --level."""
    if level:
        keys = list_by_level(vault, level.lower())
        if not keys:
            click.echo(f"No keys with visibility '{level.lower()}'.")
        else:
            for k in sorted(keys):
                click.echo(f"{k}: {level.lower()}")
    else:
        data = load_visibility(vault)
        if not data:
            click.echo("No visibility entries.")
        else:
            for k, v in sorted(data.items()):
                click.echo(f"{k}: {v}")
