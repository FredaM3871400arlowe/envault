"""CLI commands for managing key relationships."""

from pathlib import Path

import click

from envault.relationships import (
    RELATIONSHIP_TYPES,
    add_relationship,
    get_relationships,
    list_all_related_keys,
    load_relationships,
    remove_relationship,
)


@click.group("relationships")
def relationships_group() -> None:
    """Manage relationships between vault keys."""


@relationships_group.command("add")
@click.argument("vault")
@click.argument("key")
@click.argument("rel_type")
@click.argument("target")
def add_cmd(vault: str, key: str, rel_type: str, target: str) -> None:
    """Add a relationship from KEY -[REL_TYPE]-> TARGET."""
    vault_path = Path(vault)
    try:
        add_relationship(vault_path, key, rel_type, target)
        click.echo(f"Relationship added: {key} --[{rel_type}]--> {target}")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@relationships_group.command("remove")
@click.argument("vault")
@click.argument("key")
@click.argument("rel_type")
@click.argument("target")
def remove_cmd(vault: str, key: str, rel_type: str, target: str) -> None:
    """Remove a specific relationship."""
    vault_path = Path(vault)
    removed = remove_relationship(vault_path, key, rel_type, target)
    if removed:
        click.echo(f"Relationship removed: {key} --[{rel_type}]--> {target}")
    else:
        click.echo(f"No such relationship: {key} --[{rel_type}]--> {target}", err=True)
        raise SystemExit(1)


@relationships_group.command("show")
@click.argument("vault")
@click.argument("key")
def show_cmd(vault: str, key: str) -> None:
    """Show all relationships for KEY."""
    vault_path = Path(vault)
    rels = get_relationships(vault_path, key)
    if not rels:
        click.echo(f"No relationships found for '{key}'.")
        return
    for rel_type, targets in sorted(rels.items()):
        for target in targets:
            click.echo(f"  {key} --[{rel_type}]--> {target}")


@relationships_group.command("list")
@click.argument("vault")
def list_cmd(vault: str) -> None:
    """List all keys that have relationships."""
    vault_path = Path(vault)
    data = load_relationships(vault_path)
    if not data:
        click.echo("No relationships recorded.")
        return
    for key, rels in sorted(data.items()):
        for rel_type, targets in sorted(rels.items()):
            for target in targets:
                click.echo(f"  {key} --[{rel_type}]--> {target}")


@relationships_group.command("types")
def types_cmd() -> None:
    """List supported relationship types."""
    for rt in sorted(RELATIONSHIP_TYPES):
        click.echo(f"  {rt}")
