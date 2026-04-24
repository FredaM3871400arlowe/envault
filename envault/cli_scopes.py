"""CLI commands for scope management."""
from __future__ import annotations

from pathlib import Path

import click

from .scopes import VALID_SCOPES, get_scope, keys_in_scope, remove_scope, set_scope


@click.group("scope")
def scope_group() -> None:
    """Manage key scopes (dev / staging / prod …)."""


@scope_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("scope")
def set_cmd(vault: str, key: str, scope: str) -> None:
    """Assign SCOPE to KEY in VAULT."""
    path = Path(vault)
    try:
        set_scope(path, key, scope)
        click.echo(f"Scope for '{key}' set to '{scope}'.")
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@scope_group.command("get")
@click.argument("vault")
@click.argument("key")
def get_cmd(vault: str, key: str) -> None:
    """Show the scope assigned to KEY."""
    result = get_scope(Path(vault), key)
    if result is None:
        click.echo(f"No scope assigned to '{key}'.")
    else:
        click.echo(result)


@scope_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str) -> None:
    """Remove the scope assignment for KEY."""
    remove_scope(Path(vault), key)
    click.echo(f"Scope removed from '{key}'.")


@scope_group.command("list")
@click.argument("vault")
@click.option("--scope", default=None, help="Filter by a specific scope.")
def list_cmd(vault: str, scope: str | None) -> None:
    """List keys and their scopes, optionally filtered by SCOPE."""
    path = Path(vault)
    if scope:
        if scope not in VALID_SCOPES:
            click.echo(f"Unknown scope '{scope}'.", err=True)
            raise SystemExit(1)
        keys = keys_in_scope(path, scope)
        if not keys:
            click.echo(f"No keys in scope '{scope}'.")
        for k in sorted(keys):
            click.echo(f"{k}  [{scope}]")
    else:
        from .scopes import load_scopes
        scopes = load_scopes(path)
        if not scopes:
            click.echo("No scopes defined.")
        for k, s in sorted(scopes.items()):
            click.echo(f"{k}  [{s}]")
