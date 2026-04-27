"""CLI commands for key lifecycle state management."""
from __future__ import annotations

import click

from envault.lifecycle import (
    VALID_STATES,
    get_state,
    list_by_state,
    remove_state,
    set_state,
)


@click.group("lifecycle")
def lifecycle_group() -> None:
    """Manage key lifecycle states (draft/active/deprecated/archived)."""


@lifecycle_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("state", type=click.Choice(sorted(VALID_STATES), case_sensitive=False))
def set_cmd(vault: str, key: str, state: str) -> None:
    """Set lifecycle STATE for KEY in VAULT."""
    try:
        result = set_state(vault, key, state.lower())
        click.echo(f"Key '{key}' lifecycle state set to '{result}'.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@lifecycle_group.command("get")
@click.argument("vault")
@click.argument("key")
def get_cmd(vault: str, key: str) -> None:
    """Show the lifecycle state of KEY in VAULT."""
    state = get_state(vault, key)
    if state is None:
        click.echo(f"No lifecycle state set for '{key}'.")
    else:
        click.echo(state)


@lifecycle_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str) -> None:
    """Remove lifecycle state metadata for KEY."""
    remove_state(vault, key)
    click.echo(f"Lifecycle state removed for '{key}'.")


@lifecycle_group.command("list")
@click.argument("vault")
@click.argument("state", type=click.Choice(sorted(VALID_STATES), case_sensitive=False))
def list_cmd(vault: str, state: str) -> None:
    """List all keys in VAULT with the given lifecycle STATE."""
    try:
        keys = list_by_state(vault, state.lower())
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    if not keys:
        click.echo(f"No keys with state '{state}'.")
    else:
        for k in keys:
            click.echo(k)
