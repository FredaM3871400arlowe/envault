import click
from envault.hooks import load_hooks, add_hook, remove_hook, run_hooks


@click.group("hooks")
def hooks_group():
    """Manage lifecycle hooks for vault events."""


@hooks_group.command("add")
@click.argument("vault_path")
@click.option("--event", required=True, help="Event name (e.g. post-get, post-set)")
@click.option("--cmd", required=True, help="Shell command to run")
def add_cmd(vault_path, event, cmd):
    """Add a hook for a vault event."""
    try:
        add_hook(vault_path, event, cmd)
        click.echo(f"Hook added for event '{event}'.")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@hooks_group.command("remove")
@click.argument("vault_path")
@click.option("--event", required=True, help="Event name")
@click.option("--cmd", required=True, help="Shell command to remove")
def remove_cmd(vault_path, event, cmd):
    """Remove a hook for a vault event."""
    try:
        remove_hook(vault_path, event, cmd)
        click.echo(f"Hook removed for event '{event}'.")
    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@hooks_group.command("list")
@click.argument("vault_path")
def list_cmd(vault_path):
    """List all hooks for a vault."""
    hooks = load_hooks(vault_path)
    if not hooks:
        click.echo("No hooks configured.")
        return
    for event, cmds in hooks.items():
        for cmd in cmds:
            click.echo(f"{event}: {cmd}")


@hooks_group.command("run")
@click.argument("vault_path")
@click.option("--event", required=True, help="Event name to trigger")
def run_cmd(vault_path, event):
    """Manually trigger hooks for a vault event."""
    run_hooks(vault_path, event)
    click.echo(f"Hooks for '{event}' executed.")
