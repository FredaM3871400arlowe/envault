"""CLI commands for managing favourite vault keys."""

import click
from envault.favorites import (
    load_favorites,
    add_favorite,
    remove_favorite,
    list_favorites,
)
from envault.vault import read_vault


@click.group(name="favorites")
def favorites_group():
    """Manage favourite keys within a vault."""


@favorites_group.command(name="add")
@click.argument("vault")
@click.argument("key")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def add_cmd(vault: str, key: str, password: str) -> None:
    """Mark KEY as a favourite in VAULT."""
    try:
        data = read_vault(vault, password)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    if key not in data:
        raise click.ClickException(f"Key '{key}' not found in vault.")

    add_favorite(vault, key)
    click.echo(f"Added '{key}' to favourites.")


@favorites_group.command(name="remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str) -> None:
    """Remove KEY from favourites in VAULT."""
    favorites = load_favorites(vault)
    if key not in favorites:
        raise click.ClickException(f"Key '{key}' is not in favourites.")

    remove_favorite(vault, key)
    click.echo(f"Removed '{key}' from favourites.")


@favorites_group.command(name="list")
@click.argument("vault")
def list_cmd(vault: str) -> None:
    """List all favourite keys in VAULT."""
    favorites = list_favorites(vault)
    if not favorites:
        click.echo("No favourites recorded.")
        return

    click.echo(f"Favourites ({len(favorites)}):")
    for key in sorted(favorites):
        click.echo(f"  {key}")


@favorites_group.command(name="check")
@click.argument("vault")
@click.argument("key")
def check_cmd(vault: str, key: str) -> None:
    """Check whether KEY is marked as a favourite in VAULT."""
    favorites = load_favorites(vault)
    if key in favorites:
        click.echo(f"'{key}' is a favourite.")
    else:
        click.echo(f"'{key}' is not a favourite.")
