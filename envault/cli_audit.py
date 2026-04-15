"""CLI sub-commands for inspecting the vault audit log."""

from pathlib import Path

import click

from envault.audit import clear_events, read_events


@click.group("audit")
def audit_group() -> None:
    """Commands for viewing and managing the vault audit log."""


@audit_group.command("log")
@click.argument("vault", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--last",
    default=20,
    show_default=True,
    help="Number of most-recent events to display.",
)
@click.option(
    "--action",
    default=None,
    help="Filter events by action type (e.g. set, get, delete).",
)
def show_log(vault: str, last: int, action: str | None) -> None:
    """Print the audit log for VAULT."""
    events = read_events(vault)
    if action:
        events = [e for e in events if e.get("action") == action]
    events = events[-last:]
    if not events:
        click.echo("No audit events found.")
        return
    for event in events:
        key_part = f"  key={event['key']}" if "key" in event else ""
        click.echo(
            f"[{event['timestamp']}] {event['actor']:20s} {event['action']:10s}{key_part}"
        )


@audit_group.command("clear")
@click.argument("vault", type=click.Path(exists=True, dir_okay=False))
@click.confirmation_option(prompt="This will permanently delete the audit log. Continue?")
def clear_log(vault: str) -> None:
    """Delete the audit log for VAULT."""
    clear_events(vault)
    click.echo(f"Audit log cleared for {Path(vault).name}.")
