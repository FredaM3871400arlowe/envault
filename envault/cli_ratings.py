"""CLI commands for managing key ratings."""
from __future__ import annotations

import click

from envault.ratings import (
    set_rating,
    get_rating,
    remove_rating,
    list_ratings,
)


@click.group("ratings")
def ratings_group() -> None:
    """Manage key ratings (1–5)."""


@ratings_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("rating", type=int)
def set_cmd(vault: str, key: str, rating: int) -> None:
    """Set a rating (1-5) for KEY in VAULT."""
    try:
        set_rating(vault, key, rating)
        click.echo(f"Rating for '{key}' set to {rating}.")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@ratings_group.command("get")
@click.argument("vault")
@click.argument("key")
def get_cmd(vault: str, key: str) -> None:
    """Show the rating for KEY in VAULT."""
    rating = get_rating(vault, key)
    if rating is None:
        click.echo(f"No rating set for '{key}'.")
    else:
        click.echo(f"{key}: {rating}")


@ratings_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str) -> None:
    """Remove the rating for KEY in VAULT."""
    remove_rating(vault, key)
    click.echo(f"Rating for '{key}' removed.")


@ratings_group.command("list")
@click.argument("vault")
def list_cmd(vault: str) -> None:
    """List all ratings in VAULT."""
    ratings = list_ratings(vault)
    if not ratings:
        click.echo("No ratings set.")
    else:
        for k, v in sorted(ratings.items()):
            click.echo(f"{k}: {v}")
