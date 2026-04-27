"""CLI commands for managing vault key access control."""

import click
from pathlib import Path

from .access import grant, revoke, load_access, list_permitted


@click.group(name="access")
def access_group():
    """Manage access permissions for vault keys."""


@access_group.command(name="grant")
@click.argument("vault")
@click.argument("key")
@click.argument("user")
@click.option(
    "--permission",
    "-p",
    default="read",
    show_default=True,
    type=click.Choice(["read", "write", "admin"], case_sensitive=False),
    help="Permission level to grant.",
)
def grant_cmd(vault: str, key: str, user: str, permission: str):
    """Grant USER access to KEY in VAULT with the given permission level."""
    vault_path = Path(vault)
    if not vault_path.exists():
        click.echo(f"Error: vault '{vault}' not found.", err=True)
        raise SystemExit(1)

    try:
        grant(vault_path, key, user, permission.lower())
        click.echo(f"Granted '{permission}' access on '{key}' to '{user}'.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@access_group.command(name="revoke")
@click.argument("vault")
@click.argument("key")
@click.argument("user")
def revoke_cmd(vault: str, key: str, user: str):
    """Revoke USER's access to KEY in VAULT."""
    vault_path = Path(vault)
    if not vault_path.exists():
        click.echo(f"Error: vault '{vault}' not found.", err=True)
        raise SystemExit(1)

    try:
        revoke(vault_path, key, user)
        click.echo(f"Revoked access on '{key}' for '{user}'.")
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@access_group.command(name="show")
@click.argument("vault")
@click.argument("key")
def show_cmd(vault: str, key: str):
    """Show all users and their permissions for KEY in VAULT."""
    vault_path = Path(vault)
    if not vault_path.exists():
        click.echo(f"Error: vault '{vault}' not found.", err=True)
        raise SystemExit(1)

    access_data = load_access(vault_path)
    permissions = access_data.get(key, {})

    if not permissions:
        click.echo(f"No access entries found for '{key}'.")
        return

    click.echo(f"Access for '{key}':")
    for user, perm in sorted(permissions.items()):
        click.echo(f"  {user}: {perm}")


@access_group.command(name="list")
@click.argument("vault")
@click.option(
    "--user",
    "-u",
    default=None,
    help="Filter entries by user name.",
)
def list_cmd(vault: str, user: str):
    """List all access control entries in VAULT, optionally filtered by USER."""
    vault_path = Path(vault)
    if not vault_path.exists():
        click.echo(f"Error: vault '{vault}' not found.", err=True)
        raise SystemExit(1)

    access_data = load_access(vault_path)

    if not access_data:
        click.echo("No access entries defined.")
        return

    for key, permissions in sorted(access_data.items()):
        for entry_user, perm in sorted(permissions.items()):
            if user is None or entry_user == user:
                click.echo(f"{key}  {entry_user}  {perm}")


@access_group.command(name="permitted")
@click.argument("vault")
@click.argument("user")
def permitted_cmd(vault: str, user: str):
    """List all keys USER has access to in VAULT."""
    vault_path = Path(vault)
    if not vault_path.exists():
        click.echo(f"Error: vault '{vault}' not found.", err=True)
        raise SystemExit(1)

    keys = list_permitted(vault_path, user)

    if not keys:
        click.echo(f"No keys accessible by '{user}'.")
        return

    click.echo(f"Keys accessible by '{user}':")
    for key, perm in sorted(keys.items()):
        click.echo(f"  {key}: {perm}")
