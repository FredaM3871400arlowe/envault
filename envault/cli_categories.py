"""CLI commands for managing key categories."""

from __future__ import annotations

import click

from envault.categories import (
    VALID_CATEGORIES,
    get_category,
    list_by_category,
    load_categories,
    remove_category,
    set_category,
)


@click.group("categories")
def categories_group() -> None:
    """Categorise vault keys for easier organisation."""


@categories_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("category", type=click.Choice(sorted(VALID_CATEGORIES)))
def set_cmd(vault: str, key: str, category: str) -> None:
    """Assign CATEGORY to KEY in VAULT."""
    try:
        set_category(vault, key, category)
        click.echo(f"Category '{category}' set for key '{key}'.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@categories_group.command("get")
@click.argument("vault")
@click.argument("key")
def get_cmd(vault: str, key: str) -> None:
    """Show the category assigned to KEY in VAULT."""
    cat = get_category(vault, key)
    if cat is None:
        click.echo(f"No category set for key '{key}'.")
    else:
        click.echo(cat)


@categories_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str) -> None:
    """Remove the category from KEY in VAULT."""
    removed = remove_category(vault, key)
    if removed:
        click.echo(f"Category removed from key '{key}'.")
    else:
        click.echo(f"No category found for key '{key}'.")


@categories_group.command("list")
@click.argument("vault")
@click.option("--filter", "category", default=None,
              type=click.Choice(sorted(VALID_CATEGORIES)),
              help="Filter by a specific category.")
def list_cmd(vault: str, category: str | None) -> None:
    """List all key-category assignments in VAULT."""
    if category:
        keys = list_by_category(vault, category)
        if not keys:
            click.echo(f"No keys in category '{category}'.")
        else:
            for k in sorted(keys):
                click.echo(f"{k}: {category}")
    else:
        data = load_categories(vault)
        if not data:
            click.echo("No categories assigned.")
        else:
            for k, v in sorted(data.items()):
                click.echo(f"{k}: {v}")
