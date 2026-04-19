"""CLI commands for pin management."""
import click
from pathlib import Path
from envault.pins import pin_key, unpin_key, list_pins, is_pinned


@click.group("pins")
def pins_group():
    """Pin keys to protect them from deletion or overwrite."""


@pins_group.command("add")
@click.argument("vault")
@click.argument("key")
def add_cmd(vault: str, key: str):
    """Pin a key."""
    pin_key(vault, key)
    click.echo(f"Pinned '{key}'.")


@pins_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str):
    """Unpin a key."""
    try:
        unpin_key(vault, key)
        click.echo(f"Unpinned '{key}'.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@pins_group.command("list")
@click.argument("vault")
def list_cmd(vault: str):
    """List all pinned keys."""
    pins = list_pins(vault)
    if not pins:
        click.echo("No pinned keys.")
    else:
        for k in pins:
            click.echo(k)


@pins_group.command("check")
@click.argument("vault")
@click.argument("key")
def check_cmd(vault: str, key: str):
    """Check whether a key is pinned."""
    if is_pinned(vault, key):
        click.echo(f"'{key}' is pinned.")
    else:
        click.echo(f"'{key}' is not pinned.")
