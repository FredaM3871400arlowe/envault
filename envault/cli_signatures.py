"""CLI commands for managing key signatures in envault vaults."""
from __future__ import annotations

from pathlib import Path

import click

from envault.signatures import (
    sign_key,
    verify_key,
    remove_signature,
    get_signature,
    list_signed_keys,
)
from envault.vault import read_vault


@click.group("signatures")
def signatures_group() -> None:
    """Manage HMAC signatures for vault keys."""


@signatures_group.command("sign")
@click.argument("vault")
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--secret", prompt=True, hide_input=True, help="HMAC signing secret")
def sign_cmd(vault: str, key: str, password: str, secret: str) -> None:
    """Sign a key's current value with an HMAC secret."""
    vault_path = Path(vault)
    data = read_vault(vault_path, password)
    if key not in data:
        click.echo(f"Error: key '{key}' not found in vault.", err=True)
        raise SystemExit(1)
    sig = sign_key(vault_path, key, data[key], secret)
    click.echo(f"Signed '{key}': {sig}")


@signatures_group.command("verify")
@click.argument("vault")
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--secret", prompt=True, hide_input=True, help="HMAC signing secret")
def verify_cmd(vault: str, key: str, password: str, secret: str) -> None:
    """Verify a key's current value against its stored signature."""
    vault_path = Path(vault)
    data = read_vault(vault_path, password)
    if key not in data:
        click.echo(f"Error: key '{key}' not found in vault.", err=True)
        raise SystemExit(1)
    if verify_key(vault_path, key, data[key], secret):
        click.echo(f"OK: signature for '{key}' is valid.")
    else:
        click.echo(f"FAIL: signature for '{key}' is invalid or missing.", err=True)
        raise SystemExit(1)


@signatures_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str) -> None:
    """Remove the stored signature for a key."""
    vault_path = Path(vault)
    remove_signature(vault_path, key)
    click.echo(f"Removed signature for '{key}'.")


@signatures_group.command("show")
@click.argument("vault")
@click.argument("key")
def show_cmd(vault: str, key: str) -> None:
    """Show the stored signature for a key."""
    sig = get_signature(Path(vault), key)
    if sig is None:
        click.echo(f"No signature recorded for '{key}'.")
    else:
        click.echo(f"{key}: {sig}")


@signatures_group.command("list")
@click.argument("vault")
def list_cmd(vault: str) -> None:
    """List all keys that have stored signatures."""
    keys = list_signed_keys(Path(vault))
    if not keys:
        click.echo("No signatures recorded.")
    else:
        for k in keys:
            click.echo(k)
