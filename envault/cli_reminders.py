"""CLI commands for vault key reminders."""
import click
from pathlib import Path
from envault.reminders import set_reminder, get_reminder, remove_reminder, list_due, load_reminders


@click.group("reminders")
def reminders_group():
    """Manage reminders for vault keys."""


@reminders_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("due")
@click.argument("message")
def set_cmd(vault, key, due, message):
    """Set a reminder for KEY in VAULT, due on DUE (YYYY-MM-DD)."""
    try:
        set_reminder(vault, key, message, due)
        click.echo(f"Reminder set for '{key}' due {due}.")
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@reminders_group.command("show")
@click.argument("vault")
@click.argument("key")
def show_cmd(vault, key):
    """Show the reminder for KEY."""
    r = get_reminder(vault, key)
    if r is None:
        click.echo(f"No reminder for '{key}'.")
    else:
        click.echo(f"{key}: {r['message']} (due {r['due']})")


@reminders_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault, key):
    """Remove the reminder for KEY."""
    if remove_reminder(vault, key):
        click.echo(f"Reminder for '{key}' removed.")
    else:
        click.echo(f"No reminder found for '{key}'.", err=True)
        raise SystemExit(1)


@reminders_group.command("list")
@click.argument("vault")
def list_cmd(vault):
    """List all reminders in VAULT."""
    data = load_reminders(vault)
    if not data:
        click.echo("No reminders set.")
        return
    for key, info in data.items():
        click.echo(f"{key}: {info['message']} (due {info['due']})")


@reminders_group.command("due")
@click.argument("vault")
@click.option("--as-of", default=None, help="Check due as of this date (YYYY-MM-DD).")
def due_cmd(vault, as_of):
    """List reminders that are due."""
    items = list_due(vault, as_of)
    if not items:
        click.echo("No reminders due.")
        return
    for item in items:
        click.echo(f"{item['key']}: {item['message']} (due {item['due']})")
