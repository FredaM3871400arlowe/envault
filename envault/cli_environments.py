"""CLI commands for managing key environments in envault."""

from __future__ import annotations

from pathlib import Path

import click

from envault.environments import (
    VALID_ENVIRONMENTS,
    get_environment,
    list_by_environment,
    load_environments,
    remove_environment,
    set_environment,
)


@click.group("env-tag")
def environments_group() -> None:
    """Tag vault keys with deployment environments."""


@environments_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("environment")
def set_cmd(vault: str, key: str, environment: str) -> None:
    """Set the environment for a key."""
    vault_path = Path(vault)
    try:
        set_environment(vault_path, key, environment)
        click.echo(f"Key '{key}' tagged as environment '{environment}'.")
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@environments_group.command("get")
@click.argument("vault")
@click.argument("key")
def get_cmd(vault: str, key: str) -> None:
    """Show the environment for a key."""
    vault_path = Path(vault)
    env = get_environment(vault_path, key)
    if env:
        click.echo(f"{key}: {env}")
    else:
        click.echo(f"No environment set for '{key}'.")


@environments_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str) -> None:
    """Remove environment tag from a key."""
    vault_path = Path(vault)
    remove_environment(vault_path, key)
    click.echo(f"Environment tag removed from '{key}'.")


@environments_group.command("list")
@click.argument("vault")
@click.option("--filter", "env_filter", default=None, help="Filter by environment name.")
def list_cmd(vault: str, env_filter: str | None) -> None:
    """List all key-environment associations."""
    vault_path = Path(vault)
    data = load_environments(vault_path)
    if not data:
        click.echo("No environments set.")
        return
    for key, env in sorted(data.items()):
        if env_filter is None or env == env_filter:
            click.echo(f"  {key}: {env}")


@environments_group.command("find")
@click.argument("vault")
@click.argument("environment")
def find_cmd(vault: str, environment: str) -> None:
    """List all keys tagged with a given environment."""
    vault_path = Path(vault)
    if environment not in VALID_ENVIRONMENTS:
        click.echo(
            f"Unknown environment '{environment}'. "
            f"Valid: {', '.join(sorted(VALID_ENVIRONMENTS))}",
            err=True,
        )
        raise SystemExit(1)
    keys = list_by_environment(vault_path, environment)
    if keys:
        for k in keys:
            click.echo(f"  {k}")
    else:
        click.echo(f"No keys tagged as '{environment}'.")
