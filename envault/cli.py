"""Main CLI entry point for envault."""

from __future__ import annotations

import click

from envault.vault import create_vault, read_vault, update_vault, delete_key
from envault.cli_audit import audit_group
from envault.cli_profiles import profile_group
from envault.cli_rotate import rotate_group
from envault.cli_templates import template_group


@click.group()
def cli() -> None:
    """envault — secure .env vault manager."""


@cli.command("init")
@click.argument("vault")
@click.password_option(prompt="Vault password")
def init_vault(vault: str, password: str) -> None:
    """Initialise a new vault."""
    path = create_vault(vault, password, {})
    click.echo(f"Vault created: {path}")


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--vault", required=True)
@click.password_option(prompt="Vault password")
def set_key(key: str, value: str, vault: str, password: str) -> None:
    """Set a key in the vault."""
    data = read_vault(vault, password)
    data[key] = value
    update_vault(vault, password, data)
    click.echo(f"Set {key}.")


@cli.command("get")
@click.argument("key")
@click.option("--vault", required=True)
@click.option("--password", prompt=True, hide_input=True)
def get_key(key: str, vault: str, password: str) -> None:
    """Get a key from the vault."""
    data = read_vault(vault, password)
    if key not in data:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
    click.echo(data[key])


@cli.command("delete")
@click.argument("key")
@click.option("--vault", required=True)
@click.password_option(prompt="Vault password")
def delete(key: str, vault: str, password: str) -> None:
    """Delete a key from the vault."""
    delete_key(vault, password, key)
    click.echo(f"Deleted {key}.")


@cli.command("list")
@click.option("--vault", required=True)
@click.option("--password", prompt=True, hide_input=True)
def list_keys(vault: str, password: str) -> None:
    """List all keys in the vault."""
    data = read_vault(vault, password)
    if not data:
        click.echo("Vault is empty.")
        return
    for key in sorted(data):
        click.echo(key)


cli.add_command(audit_group, "audit")
cli.add_command(profile_group, "profile")
cli.add_command(rotate_group, "rotate")
cli.add_command(template_group, "template")


if __name__ == "__main__":
    cli()
