"""CLI entry point for envault using Click."""

import sys
from pathlib import Path

import click

from envault.vault import create_vault, read_vault, update_vault, delete_key
from envault.importer import import_env_file, export_vault_to_env, merge_env_file_into_vault


@click.group()
def cli():
    """envault — securely manage and sync .env files using encrypted vaults."""


@cli.command("init")
@click.argument("vault_path")
@click.password_option("--password", "-p", prompt="Vault password", help="Password to encrypt the vault.")
def init_vault(vault_path: str, password: str):
    """Create a new empty encrypted vault at VAULT_PATH."""
    path = create_vault(vault_path, password)
    click.echo(f"Vault created at {path}")


@cli.command("set")
@click.argument("vault_path")
@click.argument("key")
@click.argument("value")
@click.password_option("--password", "-p", prompt="Vault password", confirmation_prompt=False, help="Vault password.")
def set_key(vault_path: str, key: str, value: str, password: str):
    """Set KEY=VALUE in the encrypted vault."""
    try:
        update_vault(vault_path, password, {key: value})
        click.echo(f"Set {key} in {vault_path}")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("get")
@click.argument("vault_path")
@click.argument("key")
@click.password_option("--password", "-p", prompt="Vault password", confirmation_prompt=False, help="Vault password.")
def get_key(vault_path: str, key: str, password: str):
    """Print the value of KEY from the encrypted vault."""
    try:
        data = read_vault(vault_path, password)
        if key not in data:
            click.echo(f"Key '{key}' not found.", err=True)
            sys.exit(1)
        click.echo(data[key])
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("delete")
@click.argument("vault_path")
@click.argument("key")
@click.password_option("--password", "-p", prompt="Vault password", confirmation_prompt=False, help="Vault password.")
def delete(vault_path: str, key: str, password: str):
    """Delete KEY from the encrypted vault."""
    try:
        delete_key(vault_path, password, key)
        click.echo(f"Deleted '{key}' from {vault_path}")
    except (ValueError, KeyError) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("import")
@click.argument("env_file")
@click.argument("vault_path")
@click.password_option("--password", "-p", prompt="Vault password", help="Password to encrypt the vault.")
@click.option("--merge", is_flag=True, default=False, help="Merge into existing vault instead of overwriting.")
def import_cmd(env_file: str, vault_path: str, password: str, merge: bool):
    """Import an .env file into an encrypted vault."""
    try:
        if merge:
            merge_env_file_into_vault(env_file, vault_path, password)
            click.echo(f"Merged {env_file} into {vault_path}")
        else:
            import_env_file(env_file, vault_path, password)
            click.echo(f"Imported {env_file} into {vault_path}")
    except (ValueError, FileNotFoundError) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("export")
@click.argument("vault_path")
@click.argument("env_file")
@click.password_option("--password", "-p", prompt="Vault password", confirmation_prompt=False, help="Vault password.")
def export_cmd(vault_path: str, env_file: str, password: str):
    """Export an encrypted vault to a plaintext .env file."""
    try:
        export_vault_to_env(vault_path, password, env_file)
        click.echo(f"Exported {vault_path} to {env_file}")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
