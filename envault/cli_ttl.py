"""CLI commands for managing key TTLs."""

from __future__ import annotations

import click

from envault.ttl import set_ttl, get_ttl, clear_ttl, list_expired, purge_expired


@click.group("ttl")
def ttl_group():
    """Manage time-to-live settings for vault keys."""


@ttl_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("seconds", type=int)
def set_cmd(vault: str, key: str, seconds: int):
    """Set a TTL of SECONDS for KEY in VAULT."""
    try:
        expires_at = set_ttl(vault, key, seconds)
        click.echo(f"TTL set: '{key}' expires at {expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@ttl_group.command("show")
@click.argument("vault")
@click.argument("key")
def show_cmd(vault: str, key: str):
    """Show TTL expiry for KEY in VAULT."""
    dt = get_ttl(vault, key)
    if dt is None:
        click.echo(f"No TTL set for '{key}'.")
    else:
        click.echo(f"'{key}' expires at {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC")


@ttl_group.command("clear")
@click.argument("vault")
@click.argument("key")
def clear_cmd(vault: str, key: str):
    """Remove the TTL for KEY in VAULT."""
    removed = clear_ttl(vault, key)
    if removed:
        click.echo(f"TTL cleared for '{key}'.")
    else:
        click.echo(f"No TTL found for '{key}'.")


@ttl_group.command("list-expired")
@click.argument("vault")
def list_expired_cmd(vault: str):
    """List keys in VAULT whose TTL has elapsed."""
    keys = list_expired(vault)
    if not keys:
        click.echo("No expired keys.")
    else:
        for k in keys:
            click.echo(k)


@ttl_group.command("purge")
@click.argument("vault")
def purge_cmd(vault: str):
    """Purge expired TTL entries from VAULT."""
    removed = purge_expired(vault)
    if removed:
        click.echo(f"Purged {len(removed)} expired key(s): {', '.join(removed)}")
    else:
        click.echo("Nothing to purge.")
