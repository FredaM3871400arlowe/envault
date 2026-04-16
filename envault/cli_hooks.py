"""CLI commands for managing envault hooks."""
import click
from envault.hooks import add_hook, remove_hook, load_hooks


@click.group("hooks")
def hooks_group():
    """Manage pre/post event hooks for a vault."""


@hooks_group.command("add")
@click.argument("vault")
@click.argument("event")
@click.argument("command")
def add_cmd(vault: str, event: str, command: str):
    """Add a hook command for an EVENT on VAULT."""
    try:
        add_hook(vault, event, command)
        click.echo(f"Hook added for '{event}': {command}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@hooks_group.command("remove")
@click.argument("vault")
@click.argument("event")
@click.argument("command")
def remove_cmd(vault: str, event: str, command: str):
    """Remove a hook command for an EVENT on VAULT."""
    try:
        remove_hook(vault, event, command)
        click.echo(f"Hook removed for '{event}': {command}")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@hooks_group.command("list")
@click.argument("vault")
def list_cmd(vault: str):
    """List all hooks registered for VAULT."""
    hooks = load_hooks(vault)
    if not hooks:
        click.echo("No hooks registered.")
        return
    for event, cmds in sorted(hooks.items()):
        for cmd in cmds:
            click.echo(f"{event}: {cmd}")
