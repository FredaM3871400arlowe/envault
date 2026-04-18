"""CLI commands for key expiry management."""
from __future__ import annotations

from datetime import datetime, timezone

import click

from envault.expiry import set_expiry, clear_expiry, get_expiry, expired_keys, purge_expired


@click.group("expiry")
def expiry_group() -> None:
    """Manage key expiry dates."""


@expiry_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("expires_at")  # ISO format: 2025-12-31T00:00:00
def set_cmd(vault: str, key: str, expires_at: str) -> None:
    """Set an expiry date for a key (ISO 8601 format)."""
    try:
        dt = datetime.fromisoformat(expires_at)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        set_expiry(vault, key, dt)
        click.echo(f"Expiry set for '{key}': {dt.isoformat()}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@expiry_group.command("clear")
@click.argument("vault")
@click.argument("key")
def clear_cmd(vault: str, key: str) -> None:
    """Remove the expiry date for a key."""
    clear_expiry(vault, key)
    click.echo(f"Expiry cleared for '{key}'.")


@expiry_group.command("show")
@click.argument("vault")
@click.argument("key")
def show_cmd(vault: str, key: str) -> None:
    """Show the expiry date for a key."""
    dt = get_expiry(vault, key)
    if dt is None:
        click.echo(f"No expiry set for '{key}'.")
    else:
        click.echo(f"{key}: {dt.isoformat()}")


@expiry_group.command("list-expired")
@click.argument("vault")
def list_expired_cmd(vault: str) -> None:
    """List all currently expired keys."""
    keys = expired_keys(vault)
    if not keys:
        click.echo("No expired keys.")
    else:
        for k in keys:
            click.echo(k)


@expiry_group.command("purge")
@click.argument("vault")
@click.password_option("--password", prompt=True)
def purge_cmd(vault: str, password: str) -> None:
    """Delete all expired keys from the vault."""
    try:
        removed = purge_expired(vault, password)
        if removed:
            click.echo(f"Purged {len(removed)} expired key(s): {', '.join(removed)}")
        else:
            click.echo("No expired keys to purge.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
