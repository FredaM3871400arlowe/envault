"""Main CLI entry point for envault."""
from __future__ import annotations

import click

from envault.vault import create_vault, read_vault, update_vault, delete_key
from envault.cli_audit import audit_group
from envault.cli_profiles import profile_group
from envault.cli_templates import template_group
from envault.cli_hooks import hooks_group
from envault.cli_snapshots import snapshot_group
from envault.cli_tags import tags_group
from envault.cli_rotate import rotate_group
from envault.cli_watch import watch_group
from envault.cli_expiry import expiry_group


@click.group()
def cli() -> None:
    """envault — secure .env vault manager."""


@cli.command()
@click.argument("vault")
@click.password_option("--password", prompt=True)
def init_vault(vault: str, password: str) -> None:
    """Initialise a new empty vault."""
    path = create_vault(vault, password, {})
    click.echo(f"Vault created: {path}")


@cli.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("value")
@click.password_option("--password", prompt=True)
def set_key(vault: str, key: str, value: str, password: str) -> None:
    """Set a key in the vault."""
    try:
        env = read_vault(vault, password)
        env[key] = value
        update_vault(vault, password, env)
        click.echo(f"Set '{key}'.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cli.command("get")
@click.argument("vault")
@click.argument("key")
@click.password_option("--password", prompt=True)
def get_key(vault: str, key: str, password: str) -> None:
    """Get a key from the vault."""
    try:
        env = read_vault(vault, password)
        if key not in env:
            click.echo(f"Key '{key}' not found.", err=True)
            raise SystemExit(1)
        click.echo(env[key])
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument("vault")
@click.argument("key")
@click.password_option("--password", prompt=True)
def delete(vault: str, key: str, password: str) -> None:
    """Delete a key from the vault."""
    try:
        delete_key(vault, password, key)
        click.echo(f"Deleted '{key}'.")
    except (ValueError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


cli.add_command(audit_group, "audit")
cli.add_command(profile_group, "profile")
cli.add_command(template_group, "template")
cli.add_command(hooks_group, "hooks")
cli.add_command(snapshot_group, "snapshot")
cli.add_command(tags_group, "tags")
cli.add_command(rotate_group, "rotate")
cli.add_command(watch_group, "watch")
cli.add_command(expiry_group, "expiry")
