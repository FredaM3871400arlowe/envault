"""CLI commands for checksum management."""

from __future__ import annotations

import click

from envault.checksums import (
    record_checksum,
    remove_checksum,
    verify_checksum,
    verify_all,
    load_checksums,
)
from envault.vault import read_vault


@click.group("checksum")
def checksum_group() -> None:
    """Track and verify checksums for vault keys."""


@checksum_group.command("record")
@click.argument("vault")
@click.argument("key")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def record_cmd(vault: str, key: str, password: str) -> None:
    """Record a checksum for KEY using its current vault value."""
    env = read_vault(vault, password)
    if key not in env:
        raise click.ClickException(f"Key '{key}' not found in vault.")
    digest = record_checksum(vault, key, env[key])
    click.echo(f"Checksum recorded for '{key}': {digest[:12]}...")


@checksum_group.command("verify")
@click.argument("vault")
@click.argument("key")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def verify_cmd(vault: str, key: str, password: str) -> None:
    """Verify KEY's current value matches its stored checksum."""
    env = read_vault(vault, password)
    if key not in env:
        raise click.ClickException(f"Key '{key}' not found in vault.")
    ok = verify_checksum(vault, key, env[key])
    if ok:
        click.echo(f"✓ '{key}' matches stored checksum.")
    else:
        click.echo(f"✗ '{key}' does NOT match stored checksum.", err=True)
        raise SystemExit(1)


@checksum_group.command("verify-all")
@click.argument("vault")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def verify_all_cmd(vault: str, password: str) -> None:
    """Verify all tracked keys against their stored checksums."""
    env = read_vault(vault, password)
    results = verify_all(vault, env)
    if not results:
        click.echo("No checksums recorded.")
        return
    failed = [k for k, ok in results.items() if not ok]
    for key, ok in sorted(results.items()):
        mark = "✓" if ok else "✗"
        click.echo(f"  {mark} {key}")
    if failed:
        raise SystemExit(1)


@checksum_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str) -> None:
    """Remove the stored checksum for KEY."""
    remove_checksum(vault, key)
    click.echo(f"Checksum removed for '{key}'.")


@checksum_group.command("list")
@click.argument("vault")
def list_cmd(vault: str) -> None:
    """List all keys with recorded checksums."""
    data = load_checksums(vault)
    if not data:
        click.echo("No checksums recorded.")
        return
    for key, digest in sorted(data.items()):
        click.echo(f"  {key}: {digest[:12]}...")
