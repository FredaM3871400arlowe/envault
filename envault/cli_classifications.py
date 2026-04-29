"""CLI commands for key classification in envault."""
from __future__ import annotations

from pathlib import Path

import click

from envault.classifications import (
    CLASSIFICATIONS,
    auto_classify,
    get_classification,
    load_classifications,
    remove_classification,
    set_classification,
)
from envault.vault import read_vault


@click.group("classify")
def classification_group() -> None:
    """Manage semantic classifications for vault keys."""


@classification_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("classification", type=click.Choice(CLASSIFICATIONS))
def set_cmd(vault: str, key: str, classification: str) -> None:
    """Assign a classification to KEY."""
    vault_path = Path(vault)
    set_classification(vault_path, key, classification)
    click.echo(f"Classified '{key}' as '{classification}'.")


@classification_group.command("get")
@click.argument("vault")
@click.argument("key")
def get_cmd(vault: str, key: str) -> None:
    """Show the classification for KEY."""
    result = get_classification(Path(vault), key)
    if result is None:
        click.echo(f"No classification set for '{key}'.")
    else:
        click.echo(result)


@classification_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str) -> None:
    """Remove the classification for KEY."""
    remove_classification(Path(vault), key)
    click.echo(f"Removed classification for '{key}'.")


@classification_group.command("list")
@click.argument("vault")
def list_cmd(vault: str) -> None:
    """List all classified keys."""
    data = load_classifications(Path(vault))
    if not data:
        click.echo("No classifications recorded.")
        return
    for key, cls in sorted(data.items()):
        click.echo(f"{key}: {cls}")


@classification_group.command("auto")
@click.argument("vault")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def auto_cmd(vault: str, password: str) -> None:
    """Auto-classify all keys using naming heuristics."""
    vault_path = Path(vault)
    try:
        env = read_vault(vault_path, password)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    result = auto_classify(vault_path, env)
    click.echo(f"Auto-classified {len(result)} key(s).")
    for key, cls in sorted(result.items()):
        click.echo(f"  {key}: {cls}")
