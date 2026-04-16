"""CLI commands for vault password rotation."""

import click
from envault.rotate import rotate_password


@click.group("rotate")
def rotate_group():
    """Commands for rotating vault passwords."""


@rotate_group.command("password")
@click.argument("vault")
@click.option("--old-password", prompt=True, hide_input=True, help="Current vault password.")
@click.option(
    "--new-password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="New vault password.",
)
def rotate_password_cmd(vault: str, old_password: str, new_password: str):
    """Re-encrypt VAULT with a new password."""
    if old_password == new_password:
        click.echo("Error: new password must differ from the old password.", err=True)
        raise SystemExit(1)

    try:
        path = rotate_password(vault, old_password, new_password)
        click.echo(f"Password rotated successfully for {path}.")
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except ValueError:
        click.echo("Error: incorrect old password.", err=True)
        raise SystemExit(1)
