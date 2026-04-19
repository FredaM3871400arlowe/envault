"""CLI commands for the mentions feature."""
from __future__ import annotations

import glob
from pathlib import Path

import click

from envault.mentions import scan_files, get_mentions, load_mentions, clear_mentions
from envault.vault import read_vault


@click.group("mentions")
def mentions_group() -> None:
    """Track which source files reference vault keys."""


@mentions_group.command("scan")
@click.argument("vault")
@click.argument("globs", nargs=-1, required=True)
@click.option("--password", prompt=True, hide_input=True)
def scan_cmd(vault: str, globs: tuple, password: str) -> None:
    """Scan files matching GLOBS for vault key references."""
    try:
        data = read_vault(vault, password)
    except ValueError as exc:
        raise click.ClickException(str(exc))

    paths = []
    for pattern in globs:
        paths.extend(glob.glob(pattern, recursive=True))

    if not paths:
        click.echo("No files matched the provided globs.")
        return

    results = scan_files(vault, paths, list(data.keys()))
    total = sum(len(v) for v in results.values())
    click.echo(f"Scanned {len(paths)} file(s). Found {total} mention(s) across {len(results)} key(s).")


@mentions_group.command("show")
@click.argument("vault")
@click.argument("key")
def show_cmd(vault: str, key: str) -> None:
    """Show files that mention KEY."""
    files = get_mentions(vault, key)
    if not files:
        click.echo(f"No recorded mentions for '{key}'.")
        return
    click.echo(f"Key '{key}' mentioned in:")
    for f in files:
        click.echo(f"  {f}")


@mentions_group.command("list")
@click.argument("vault")
def list_cmd(vault: str) -> None:
    """List all keys with recorded mentions."""
    data = load_mentions(vault)
    if not data:
        click.echo("No mention data recorded.")
        return
    for key, files in data.items():
        click.echo(f"{key}: {len(files)} file(s)")


@mentions_group.command("clear")
@click.argument("vault")
def clear_cmd(vault: str) -> None:
    """Clear all recorded mention data."""
    clear_mentions(vault)
    click.echo("Mention data cleared.")
