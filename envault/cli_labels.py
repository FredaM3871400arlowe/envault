"""CLI commands for managing key labels."""
import click
from envault.labels import set_label, get_label, remove_label, list_labels


@click.group("labels")
def labels_group() -> None:
    """Attach human-readable labels to vault keys."""


@labels_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("label")
def set_cmd(vault: str, key: str, label: str) -> None:
    """Set a display label for KEY."""
    try:
        set_label(vault, key, label)
        click.echo(f"Label for '{key}' set to '{label}'.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@labels_group.command("get")
@click.argument("vault")
@click.argument("key")
def get_cmd(vault: str, key: str) -> None:
    """Show the label for KEY."""
    label = get_label(vault, key)
    if label is None:
        click.echo(f"No label set for '{key}'.")
    else:
        click.echo(label)


@labels_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str) -> None:
    """Remove the label for KEY."""
    remove_label(vault, key)
    click.echo(f"Label for '{key}' removed.")


@labels_group.command("list")
@click.argument("vault")
def list_cmd(vault: str) -> None:
    """List all labels in the vault."""
    labels = list_labels(vault)
    if not labels:
        click.echo("No labels defined.")
    else:
        for key, label in sorted(labels.items()):
            click.echo(f"{key}: {label}")
