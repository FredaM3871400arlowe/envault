"""CLI commands for managing key priority levels."""
from __future__ import annotations

import click

from envault.priorities import (
    VALID_PRIORITIES,
    get_priority,
    list_by_priority,
    load_priorities,
    remove_priority,
    set_priority,
)


@click.group("priorities")
def priorities_group() -> None:
    """Manage priority levels for vault keys."""


@priorities_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("priority", type=click.Choice(sorted(VALID_PRIORITIES), case_sensitive=False))
def set_cmd(vault: str, key: str, priority: str) -> None:
    """Set the priority level for KEY in VAULT."""
    try:
        set_priority(vault, key, priority)
        click.echo(f"Priority for '{key}' set to '{priority.lower()}'.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@priorities_group.command("get")
@click.argument("vault")
@click.argument("key")
def get_cmd(vault: str, key: str) -> None:
    """Show the priority level for KEY in VAULT."""
    priority = get_priority(vault, key)
    if priority is None:
        click.echo(f"No priority set for '{key}'.")
    else:
        click.echo(priority)


@priorities_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str) -> None:
    """Remove the priority for KEY in VAULT."""
    removed = remove_priority(vault, key)
    if removed:
        click.echo(f"Priority for '{key}' removed.")
    else:
        click.echo(f"No priority found for '{key}'.", err=True)
        raise SystemExit(1)


@priorities_group.command("list")
@click.argument("vault")
@click.option("--filter", "priority_filter", default=None,
              type=click.Choice(sorted(VALID_PRIORITIES), case_sensitive=False),
              help="Filter keys by priority level.")
def list_cmd(vault: str, priority_filter: str | None) -> None:
    """List all key priorities in VAULT."""
    if priority_filter:
        keys = list_by_priority(vault, priority_filter)
        if not keys:
            click.echo(f"No keys with priority '{priority_filter}'.")
        else:
            for key in keys:
                click.echo(f"{key}: {priority_filter}")
    else:
        data = load_priorities(vault)
        if not data:
            click.echo("No priorities set.")
        else:
            for key, prio in sorted(data.items()):
                click.echo(f"{key}: {prio}")
