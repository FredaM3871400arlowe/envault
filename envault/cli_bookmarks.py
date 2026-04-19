"""CLI commands for managing vault key bookmarks."""
import click
from pathlib import Path
from envault.bookmarks import add_bookmark, remove_bookmark, resolve_bookmark, list_bookmarks


@click.group("bookmarks")
def bookmarks_group():
    """Manage bookmarks for vault keys."""


@bookmarks_group.command("add")
@click.argument("name")
@click.argument("key")
@click.option("--vault", required=True, help="Path to the vault file.")
def add_cmd(name: str, key: str, vault: str):
    """Add a bookmark NAME pointing to KEY."""
    try:
        add_bookmark(vault, name, key)
        click.echo(f"Bookmark '{name}' -> '{key}' added.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@bookmarks_group.command("remove")
@click.argument("name")
@click.option("--vault", required=True, help="Path to the vault file.")
def remove_cmd(name: str, vault: str):
    """Remove bookmark NAME."""
    try:
        remove_bookmark(vault, name)
        click.echo(f"Bookmark '{name}' removed.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@bookmarks_group.command("resolve")
@click.argument("name")
@click.option("--vault", required=True, help="Path to the vault file.")
def resolve_cmd(name: str, vault: str):
    """Show the key that bookmark NAME points to."""
    try:
        key = resolve_bookmark(vault, name)
        click.echo(key)
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@bookmarks_group.command("list")
@click.option("--vault", required=True, help="Path to the vault file.")
def list_cmd(vault: str):
    """List all bookmarks."""
    bm = list_bookmarks(vault)
    if not bm:
        click.echo("No bookmarks defined.")
        return
    for name, key in bm.items():
        click.echo(f"{name} -> {key}")
