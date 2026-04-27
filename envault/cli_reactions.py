"""CLI commands for managing key reactions."""
from __future__ import annotations

from pathlib import Path

import click

from .reactions import (
    VALID_REACTIONS,
    add_reaction,
    clear_reactions,
    get_reactions,
    load_reactions,
    remove_reaction,
)


@click.group("reactions")
def reactions_group() -> None:
    """Attach emoji reactions to vault keys."""


@reactions_group.command("add")
@click.argument("vault")
@click.argument("key")
@click.argument("reaction")
def add_cmd(vault: str, key: str, reaction: str) -> None:
    """Add a reaction to a key."""
    try:
        result = add_reaction(Path(vault), key, reaction)
        click.echo(f"Reaction {reaction} added to '{key}'. Current: {' '.join(result)}")
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@reactions_group.command("remove")
@click.argument("vault")
@click.argument("key")
@click.argument("reaction")
def remove_cmd(vault: str, key: str, reaction: str) -> None:
    """Remove a reaction from a key."""
    result = remove_reaction(Path(vault), key, reaction)
    remaining = " ".join(result) if result else "(none)"
    click.echo(f"Reaction {reaction} removed from '{key}'. Remaining: {remaining}")


@reactions_group.command("show")
@click.argument("vault")
@click.argument("key")
def show_cmd(vault: str, key: str) -> None:
    """Show all reactions for a key."""
    reactions = get_reactions(Path(vault), key)
    if reactions:
        click.echo(f"{key}: {' '.join(reactions)}")
    else:
        click.echo(f"No reactions for '{key}'.")


@reactions_group.command("list")
@click.argument("vault")
def list_cmd(vault: str) -> None:
    """List all keys that have reactions."""
    data = load_reactions(Path(vault))
    if not data:
        click.echo("No reactions recorded.")
        return
    for key, reactions in sorted(data.items()):
        click.echo(f"  {key}: {' '.join(reactions)}")


@reactions_group.command("clear")
@click.argument("vault")
@click.argument("key")
def clear_cmd(vault: str, key: str) -> None:
    """Remove all reactions from a key."""
    clear_reactions(Path(vault), key)
    click.echo(f"All reactions cleared for '{key}'.")
