"""CLI commands for managing vault key approval workflows."""
import click
from pathlib import Path

from envault.approvals import (
    request_approval,
    review_approval,
    get_approval,
    remove_approval,
    list_pending,
    load_approvals,
)


@click.group("approvals")
def approvals_group():
    """Manage approval workflows for key changes."""


@approvals_group.command("request")
@click.argument("vault")
@click.argument("key")
@click.option("--requestor", required=True, help="Name/ID of the requestor.")
@click.option("--reason", default="", help="Reason for the change request.")
def request_cmd(vault, key, requestor, reason):
    """Request approval for a key change."""
    entry = request_approval(Path(vault), key, requestor, reason)
    click.echo(f"Approval requested for '{key}' by '{requestor}' (state: {entry['state']}).")


@approvals_group.command("approve")
@click.argument("vault")
@click.argument("key")
@click.option("--reviewer", required=True, help="Name/ID of the reviewer.")
def approve_cmd(vault, key, reviewer):
    """Approve a pending key change request."""
    try:
        entry = review_approval(Path(vault), key, reviewer, approve=True)
        click.echo(f"'{key}' approved by '{reviewer}'.")
    except (KeyError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@approvals_group.command("reject")
@click.argument("vault")
@click.argument("key")
@click.option("--reviewer", required=True, help="Name/ID of the reviewer.")
def reject_cmd(vault, key, reviewer):
    """Reject a pending key change request."""
    try:
        entry = review_approval(Path(vault), key, reviewer, approve=False)
        click.echo(f"'{key}' rejected by '{reviewer}'.")
    except (KeyError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@approvals_group.command("show")
@click.argument("vault")
@click.argument("key")
def show_cmd(vault, key):
    """Show the approval status for a key."""
    entry = get_approval(Path(vault), key)
    if entry is None:
        click.echo(f"No approval record for '{key}'.")
    else:
        click.echo(f"Key:        {key}")
        click.echo(f"State:      {entry['state']}")
        click.echo(f"Requestor:  {entry['requestor']}")
        click.echo(f"Reason:     {entry['reason'] or '(none)'}")
        click.echo(f"Requested:  {entry['requested_at']}")
        if entry['reviewed_by']:
            click.echo(f"Reviewed by: {entry['reviewed_by']} at {entry['reviewed_at']}")


@approvals_group.command("list")
@click.argument("vault")
@click.option("--pending", is_flag=True, help="Show only pending approvals.")
def list_cmd(vault, pending):
    """List all approval records (or only pending ones)."""
    data = list_pending(Path(vault)) if pending else load_approvals(Path(vault))
    if not data:
        click.echo("No approval records found.")
    else:
        for key, entry in data.items():
            click.echo(f"{key}: {entry['state']} (requestor: {entry['requestor']})")


@approvals_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault, key):
    """Remove an approval record for a key."""
    remove_approval(Path(vault), key)
    click.echo(f"Approval record for '{key}' removed.")
