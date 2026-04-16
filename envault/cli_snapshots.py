"""CLI commands for vault snapshots."""
import click

from envault.snapshots import (
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
    take_snapshot,
)
from envault.vault import create_vault


@click.group("snapshot")
def snapshot_group() -> None:
    """Manage vault snapshots."""


@snapshot_group.command("take")
@click.argument("vault")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--label", default="", help="Optional label for the snapshot.")
def take_cmd(vault: str, password: str, label: str) -> None:
    """Take a snapshot of the current vault state."""
    try:
        snap = take_snapshot(vault, password, label=label)
        ts = snap["timestamp"]
        click.echo(f"Snapshot taken at {ts}" + (f" [{label}]" if label else ""))
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@snapshot_group.command("list")
@click.argument("vault")
def list_cmd(vault: str) -> None:
    """List all snapshots for a vault."""
    snaps = list_snapshots(vault)
    if not snaps:
        click.echo("No snapshots found.")
        return
    for s in snaps:
        label = f" [{s['label']}]" if s["label"] else ""
        click.echo(f"[{s['index']}] {s['timestamp']}{label}")


@snapshot_group.command("restore")
@click.argument("vault")
@click.argument("index", type=int)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--new-password", prompt="New vault password", hide_input=True, confirmation_prompt=True)
def restore_cmd(vault: str, index: int, password: str, new_password: str) -> None:
    """Restore vault to a previous snapshot (creates a new vault file)."""
    try:
        data = restore_snapshot(vault, password, index)
        create_vault(vault, new_password, initial_data=data)
        click.echo(f"Vault restored from snapshot {index}.")
    except (IndexError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@snapshot_group.command("delete")
@click.argument("vault")
@click.argument("index", type=int)
def delete_cmd(vault: str, index: int) -> None:
    """Delete a snapshot by index."""
    try:
        delete_snapshot(vault, index)
        click.echo(f"Snapshot {index} deleted.")
    except IndexError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
