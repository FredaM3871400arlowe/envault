"""CLI commands for vault key change-frequency trends."""

from __future__ import annotations

from pathlib import Path

import click

from .trends import (
    clear_trends,
    get_change_count,
    get_most_changed,
    load_trends,
    record_change,
)


@click.group("trends")
def trends_group() -> None:
    """Inspect change-frequency trends for vault keys."""


@trends_group.command("record")
@click.argument("vault")
@click.argument("key")
def record_cmd(vault: str, key: str) -> None:
    """Record a change event for KEY in VAULT."""
    ts = record_change(Path(vault), key)
    click.echo(f"Recorded change for '{key}' at {ts}.")


@trends_group.command("count")
@click.argument("vault")
@click.argument("key")
def count_cmd(vault: str, key: str) -> None:
    """Show how many times KEY has been changed."""
    n = get_change_count(Path(vault), key)
    click.echo(f"'{key}' has been changed {n} time(s).")


@trends_group.command("top")
@click.argument("vault")
@click.option("--n", default=5, show_default=True, help="Number of keys to show.")
def top_cmd(vault: str, n: int) -> None:
    """Show the most frequently changed keys."""
    results = get_most_changed(Path(vault), top_n=n)
    if not results:
        click.echo("No trend data recorded yet.")
        return
    for key, count in results:
        click.echo(f"{key}: {count} change(s)")


@trends_group.command("list")
@click.argument("vault")
def list_cmd(vault: str) -> None:
    """List all keys that have trend data."""
    data = load_trends(Path(vault))
    if not data:
        click.echo("No trend data recorded.")
        return
    for key, timestamps in sorted(data.items()):
        click.echo(f"{key}: {len(timestamps)} change(s)")


@trends_group.command("clear")
@click.argument("vault")
@click.argument("key")
def clear_cmd(vault: str, key: str) -> None:
    """Clear trend history for KEY."""
    removed = clear_trends(Path(vault), key)
    if removed:
        click.echo(f"Trend history cleared for '{key}'.")
    else:
        click.echo(f"No trend data found for '{key}'.")
        raise SystemExit(1)
