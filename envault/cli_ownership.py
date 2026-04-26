"""CLI commands for vault key ownership management."""

from __future__ import annotations

from pathlib import Path

import click

from .ownership import (
    get_owner,
    list_by_owner,
    load_ownership,
    remove_owner,
    set_owner,
)


@click.group("ownership")
def ownership_group() -> None:
    """Manage ownership of vault keys."""


@ownership_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("owner")
def set_cmd(vault: str, key: str, owner: str) -> None:
    """Assign OWNER to KEY in VAULT."""
    vault_path = Path(vault)
    set_owner(vault_path, key, owner)
    click.echo(f"Owner of '{key}' set to '{owner}'.")


@ownership_group.command("get")
@click.argument("vault")
@click.argument("key")
def get_cmd(vault: str, key: str) -> None:
    """Show the owner of KEY in VAULT."""
    owner = get_owner(Path(vault), key)
    if owner is None:
        click.echo(f"No owner set for '{key}'.")
    else:
        click.echo(owner)


@ownership_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str) -> None:
    """Remove ownership metadata for KEY in VAULT."""
    remove_owner(Path(vault), key)
    click.echo(f"Ownership removed for '{key}'.")


@ownership_group.command("list")
@click.argument("vault")
@click.option("--owner", default=None, help="Filter keys by owner.")
def list_cmd(vault: str, owner: str | None) -> None:
    """List ownership entries in VAULT."""
    vault_path = Path(vault)
    if owner:
        keys = list_by_owner(vault_path, owner)
        if not keys:
            click.echo(f"No keys owned by '{owner}'.")
        else:
            for k in keys:
                click.echo(f"{k}  ->  {owner}")
    else:
        data = load_ownership(vault_path)
        if not data:
            click.echo("No ownership entries found.")
        else:
            for k, v in data.items():
                click.echo(f"{k}  ->  {v}")
