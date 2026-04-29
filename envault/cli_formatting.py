"""CLI commands for managing key formatting rules."""
import click
from pathlib import Path

from envault.formatting import (
    FORMATS,
    set_format,
    get_format,
    remove_format,
    list_formats,
    apply_format,
)
from envault.vault import read_vault


@click.group("formatting")
def formatting_group():
    """Manage value formatting rules for vault keys."""


@formatting_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("fmt", metavar="FORMAT")
def set_cmd(vault: str, key: str, fmt: str):
    """Set a formatting rule for KEY (upper|lower|title|strip|none)."""
    try:
        set_format(Path(vault), key, fmt)
        click.echo(f"Format for '{key}' set to '{fmt}'.")
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@formatting_group.command("get")
@click.argument("vault")
@click.argument("key")
def get_cmd(vault: str, key: str):
    """Show the formatting rule for KEY."""
    fmt = get_format(Path(vault), key)
    if fmt is None:
        click.echo(f"No formatting rule for '{key}'.")
    else:
        click.echo(fmt)


@formatting_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str):
    """Remove the formatting rule for KEY."""
    remove_format(Path(vault), key)
    click.echo(f"Formatting rule for '{key}' removed.")


@formatting_group.command("list")
@click.argument("vault")
def list_cmd(vault: str):
    """List all formatting rules in the vault."""
    rules = list_formats(Path(vault))
    if not rules:
        click.echo("No formatting rules defined.")
    else:
        for k, v in sorted(rules.items()):
            click.echo(f"  {k}: {v}")


@formatting_group.command("preview")
@click.argument("vault")
@click.argument("key")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def preview_cmd(vault: str, key: str, password: str):
    """Preview the formatted value of KEY from the vault."""
    try:
        data = read_vault(Path(vault), password)
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    if key not in data:
        click.echo(f"Key '{key}' not found in vault.", err=True)
        raise SystemExit(1)
    fmt = get_format(Path(vault), key) or "none"
    raw = data[key]
    formatted = apply_format(raw, fmt)
    click.echo(f"raw:       {raw}")
    click.echo(f"format:    {fmt}")
    click.echo(f"formatted: {formatted}")
