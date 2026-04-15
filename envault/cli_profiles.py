"""CLI commands for managing envault profiles."""

from __future__ import annotations

from pathlib import Path

import click

from envault.profiles import (
    add_profile,
    get_profile,
    list_profiles,
    remove_profile,
)


@click.group("profile")
def profile_group() -> None:
    """Manage named vault profiles (dev, staging, prod …)."""


@profile_group.command("add")
@click.argument("name")
@click.argument("vault_path", type=click.Path())
def add_cmd(name: str, vault_path: str) -> None:
    """Register a named profile pointing to VAULT_PATH."""
    add_profile(name, vault_path)
    click.echo(f"Profile '{name}' -> {vault_path} saved.")


@profile_group.command("remove")
@click.argument("name")
def remove_cmd(name: str) -> None:
    """Delete a named profile."""
    try:
        remove_profile(name)
        click.echo(f"Profile '{name}' removed.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@profile_group.command("list")
def list_cmd() -> None:
    """List all registered profiles."""
    names = list_profiles()
    if not names:
        click.echo("No profiles defined.")
        return
    for name in names:
        info = get_profile(name)
        click.echo(f"  {name:20s}  {info['vault']}")


@profile_group.command("show")
@click.argument("name")
def show_cmd(name: str) -> None:
    """Show details of a single profile."""
    try:
        info = get_profile(name)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"name : {name}")
    click.echo(f"vault: {info['vault']}")
