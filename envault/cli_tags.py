"""CLI commands for tag management."""
import click
from envault.tags import add_tag, remove_tag, get_tags, keys_with_tag


@click.group("tags")
def tags_group():
    """Manage tags on vault keys."""


@tags_group.command("add")
@click.argument("vault")
@click.argument("key")
@click.argument("tag")
def add_cmd(vault: str, key: str, tag: str):
    """Add TAG to KEY in VAULT."""
    add_tag(vault, key, tag)
    click.echo(f"Tagged '{key}' with '{tag}'.")


@tags_group.command("remove")
@click.argument("vault")
@click.argument("key")
@click.argument("tag")
def remove_cmd(vault: str, key: str, tag: str):
    """Remove TAG from KEY in VAULT."""
    try:
        remove_tag(vault, key, tag)
        click.echo(f"Removed tag '{tag}' from '{key}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@tags_group.command("list")
@click.argument("vault")
@click.argument("key")
def list_cmd(vault: str, key: str):
    """List tags on KEY in VAULT."""
    tags = get_tags(vault, key)
    if not tags:
        click.echo(f"No tags on '{key}'.")
    else:
        for t in tags:
            click.echo(t)


@tags_group.command("find")
@click.argument("vault")
@click.argument("tag")
def find_cmd(vault: str, tag: str):
    """Find all keys with TAG in VAULT."""
    keys = keys_with_tag(vault, tag)
    if not keys:
        click.echo(f"No keys tagged '{tag}'.")
    else:
        for k in keys:
            click.echo(k)
