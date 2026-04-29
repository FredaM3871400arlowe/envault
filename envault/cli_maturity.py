"""CLI commands for vault key maturity analysis."""

from __future__ import annotations

from pathlib import Path

import click

from envault.maturity import (
    MATURITY_LEVELS,
    compute_maturity,
    get_maturity,
    load_maturity,
)
from envault.vault import read_vault
from envault.history import load_history


@click.group("maturity")
def maturity_group() -> None:
    """Analyse and inspect key maturity levels."""


@maturity_group.command("analyse")
@click.argument("vault")
@click.password_option("--password", "-p", prompt=True, help="Vault password.")
def analyse_cmd(vault: str, password: str) -> None:
    """Compute maturity for all keys in VAULT."""
    vault_path = Path(vault)
    try:
        data = read_vault(vault_path, password)
    except ValueError as exc:
        raise click.ClickException(str(exc))

    history = load_history(vault_path)
    results = compute_maturity(vault_path, list(data.keys()), history)
    click.echo(f"Analysed {len(results)} key(s).")
    for r in sorted(results.values(), key=lambda x: x.key):
        click.echo(f"  {r.key}: {r.level} (age={r.age_days}d, changes={r.change_count})")


@maturity_group.command("show")
@click.argument("vault")
@click.argument("key")
def show_cmd(vault: str, key: str) -> None:
    """Show maturity details for KEY in VAULT."""
    vault_path = Path(vault)
    result = get_maturity(vault_path, key)
    if result is None:
        click.echo(f"No maturity data for '{key}'. Run 'maturity analyse' first.")
        return
    click.echo(f"Key:          {result.key}")
    click.echo(f"Level:        {result.level}")
    click.echo(f"Age (days):   {result.age_days}")
    click.echo(f"Changes:      {result.change_count}")
    click.echo(f"Last seen:    {result.last_seen}")


@maturity_group.command("list")
@click.argument("vault")
@click.option("--level", type=click.Choice(MATURITY_LEVELS), default=None,
              help="Filter by maturity level.")
def list_cmd(vault: str, level: str | None) -> None:
    """List all keys with their maturity level."""
    vault_path = Path(vault)
    data = load_maturity(vault_path)
    if not data:
        click.echo("No maturity data found. Run 'maturity analyse' first.")
        return
    for key, info in sorted(data.items()):
        if level and info["level"] != level:
            continue
        click.echo(f"{key}: {info['level']}")
