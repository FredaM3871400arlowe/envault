"""CLI commands for inspecting vault key change history."""
import click
from envault.history import get_history, clear_history, load_history


@click.group("history")
def history_group():
    """View and manage key change history."""


@history_group.command("show")
@click.argument("vault")
@click.argument("key")
@click.option("--last", default=0, help="Show only the last N entries.")
def show_cmd(vault: str, key: str, last: int):
    """Show change history for KEY in VAULT."""
    records = get_history(vault, key)
    if not records:
        click.echo(f"No history found for '{key}'.")
        return
    if last:
        records = records[-last:]
    for i, r in enumerate(records, 1):
        click.echo(f"[{i}] {r['timestamp']}")
        click.echo(f"    old: {r['old']}")
        click.echo(f"    new: {r['new']}")


@history_group.command("list")
@click.argument("vault")
def list_cmd(vault: str):
    """List all keys that have recorded history in VAULT."""
    history = load_history(vault)
    if not history:
        click.echo("No history recorded.")
        return
    for key, records in history.items():
        click.echo(f"{key}: {len(records)} change(s)")


@history_group.command("clear")
@click.argument("vault")
@click.option("--key", default=None, help="Clear history for a specific key only.")
@click.confirmation_option(prompt="Are you sure you want to clear history?")
def clear_cmd(vault: str, key: str | None):
    """Clear history for VAULT (or a single KEY)."""
    clear_history(vault, key)
    target = f"'{key}'" if key else "all keys"
    click.echo(f"History cleared for {target}.")
