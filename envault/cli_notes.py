"""CLI commands for managing per-key notes."""
import click
from envault.notes import set_note, get_note, remove_note, list_notes


@click.group("notes")
def notes_group():
    """Manage notes attached to vault keys."""


@notes_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("note")
def set_cmd(vault: str, key: str, note: str):
    """Attach a note to KEY in VAULT."""
    set_note(vault, key, note)
    click.echo(f"Note set for '{key}'.")


@notes_group.command("get")
@click.argument("vault")
@click.argument("key")
def get_cmd(vault: str, key: str):
    """Show the note for KEY in VAULT."""
    note = get_note(vault, key)
    if note is None:
        click.echo(f"No note for '{key}'.")
    else:
        click.echo(note)


@notes_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str):
    """Remove the note for KEY in VAULT."""
    try:
        remove_note(vault, key)
        click.echo(f"Note removed for '{key}'.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@notes_group.command("list")
@click.argument("vault")
def list_cmd(vault: str):
    """List all notes in VAULT."""
    notes = list_notes(vault)
    if not notes:
        click.echo("No notes found.")
    else:
        for key, note in notes.items():
            click.echo(f"{key}: {note}")
