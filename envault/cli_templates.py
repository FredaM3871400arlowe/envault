"""CLI commands for template management."""

from __future__ import annotations

from pathlib import Path

import click

from envault.templates import (
    add_template,
    remove_template,
    load_templates,
    get_template,
)


@click.group("template")
def template_group() -> None:
    """Manage env key templates."""


@template_group.command("add")
@click.argument("name")
@click.argument("keys", nargs=-1, required=True)
@click.option("--vault", required=True, help="Path to vault file.")
def add_cmd(name: str, keys: tuple, vault: str) -> None:
    """Create a template with the given KEYS."""
    base = Path(vault).parent
    try:
        add_template(base, name, list(keys))
        click.echo(f"Template '{name}' saved with {len(keys)} key(s).")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)


@template_group.command("remove")
@click.argument("name")
@click.option("--vault", required=True, help="Path to vault file.")
def remove_cmd(name: str, vault: str) -> None:
    """Delete a template."""
    base = Path(vault).parent
    try:
        remove_template(base, name)
        click.echo(f"Template '{name}' removed.")
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)


@template_group.command("list")
@click.option("--vault", required=True, help="Path to vault file.")
def list_cmd(vault: str) -> None:
    """List all templates."""
    base = Path(vault).parent
    templates = load_templates(base)
    if not templates:
        click.echo("No templates defined.")
        return
    for name, keys in templates.items():
        click.echo(f"{name}: {', '.join(keys)}")


@template_group.command("show")
@click.argument("name")
@click.option("--vault", required=True, help="Path to vault file.")
def show_cmd(name: str, vault: str) -> None:
    """Show keys in a template."""
    base = Path(vault).parent
    try:
        keys = get_template(base, name)
        click.echo("\n".join(keys))
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
