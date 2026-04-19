"""CLI commands for managing key groups."""
import click
from envault.groups import (
    add_to_group,
    remove_from_group,
    delete_group,
    get_group,
    list_groups,
)


@click.group("groups")
def groups_group():
    """Organise vault keys into named groups."""


@groups_group.command("add")
@click.argument("vault")
@click.argument("group")
@click.argument("key")
def add_cmd(vault, group, key):
    """Add KEY to GROUP in VAULT."""
    try:
        add_to_group(vault, group, key)
        click.echo(f"Added '{key}' to group '{group}'.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@groups_group.command("remove")
@click.argument("vault")
@click.argument("group")
@click.argument("key")
def remove_cmd(vault, group, key):
    """Remove KEY from GROUP in VAULT."""
    try:
        remove_from_group(vault, group, key)
        click.echo(f"Removed '{key}' from group '{group}'.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@groups_group.command("delete")
@click.argument("vault")
@click.argument("group")
def delete_cmd(vault, group):
    """Delete an entire GROUP from VAULT."""
    try:
        delete_group(vault, group)
        click.echo(f"Deleted group '{group}'.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@groups_group.command("show")
@click.argument("vault")
@click.argument("group")
def show_cmd(vault, group):
    """Show all keys in GROUP."""
    try:
        keys = get_group(vault, group)
        if keys:
            click.echo("\n".join(keys))
        else:
            click.echo(f"Group '{group}' is empty.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@groups_group.command("list")
@click.argument("vault")
def list_cmd(vault):
    """List all groups in VAULT."""
    groups = list_groups(vault)
    if groups:
        click.echo("\n".join(groups))
    else:
        click.echo("No groups defined.")
