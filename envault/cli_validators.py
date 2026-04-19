"""CLI commands for vault validation."""
from __future__ import annotations
import click
from envault.vault import read_vault
from envault.validators import validate_dict, format_report


@click.group("validate")
def validate_group():
    """Validate vault key/value entries."""


@validate_group.command("run")
@click.argument("vault")
@click.password_option("--password", "-p", prompt="Vault password", confirmation_prompt=False)
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero if any issues found.")
def run_cmd(vault: str, password: str, strict: bool):
    """Run all validation rules against VAULT."""
    try:
        data = read_vault(vault, password)
    except ValueError as exc:
        raise click.ClickException(str(exc))

    report = validate_dict(data)
    click.echo(format_report(report))

    if strict and not report.ok:
        raise SystemExit(1)


@validate_group.command("check-key")
@click.argument("vault")
@click.argument("key")
@click.password_option("--password", "-p", prompt="Vault password", confirmation_prompt=False)
def check_key_cmd(vault: str, key: str, password: str):
    """Validate a single KEY in VAULT."""
    try:
        data = read_vault(vault, password)
    except ValueError as exc:
        raise click.ClickException(str(exc))

    if key not in data:
        raise click.ClickException(f"Key '{key}' not found in vault.")

    report = validate_dict({key: data[key]})
    click.echo(format_report(report))
