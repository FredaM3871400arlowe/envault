"""CLI commands for managing key aliases."""
from __future__ import annotations

import click

from envault.aliases import add_alias, remove_alias, list_aliases, resolve_alias


@click.group("alias")
def alias_group() -> None:
    """Manage friendly aliases for vault keys."""


@alias_group.command("add")
@click.argument("alias")
@click.argument("key")
@click.option("--vault", required=True, help="Path to vault file")
def add_cmd(alias: str, key: str, vault: str) -> None:
    """Map ALIAS to KEY inside the vault."""
    try:
        add_alias(vault, alias, key)
        click.echo(f"Alias '{alias}' -> '{key}' added.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@alias_group.command("remove")
@click.argument("alias")
@click.option("--vault", required=True, help="Path to vault file")
def remove_cmd(alias: str, vault: str) -> None:
    """Remove an alias."""
    try:
        remove_alias(vault, alias)
        click.echo(f"Alias '{alias}' removed.")
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@alias_group.command("list")
@click.option("--vault", required=True, help="Path to vault file")
def list_cmd(vault: str) -> None:
    """List all aliases."""
    aliases = list_aliases(vault)
    if not aliases:
        click.echo("No aliases defined.")
        return
    for alias, key in aliases.items():
        click.echo(f"  {alias} -> {key}")


@alias_group.command("resolve")
@click.argument("alias")
@click.option("--vault", required=True, help="Path to vault file")
def resolve_cmd(alias: str, vault: str) -> None:
    """Show the vault key that ALIAS maps to."""
    key = resolve_alias(vault, alias)
    click.echo(key)
