"""CLI commands for managing key namespaces."""

from __future__ import annotations

from pathlib import Path

import click

from envault.namespaces import (
    get_namespace,
    keys_in_namespace,
    list_namespaces,
    remove_namespace,
    set_namespace,
)


@click.group("namespace")
def namespace_group() -> None:
    """Manage key namespaces."""


@namespace_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.argument("namespace")
def set_cmd(vault: str, key: str, namespace: str) -> None:
    """Assign KEY to NAMESPACE inside VAULT."""
    vault_path = Path(vault)
    try:
        set_namespace(vault_path, key, namespace)
        click.echo(f"Key '{key}' assigned to namespace '{namespace}'.")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@namespace_group.command("get")
@click.argument("vault")
@click.argument("key")
def get_cmd(vault: str, key: str) -> None:
    """Show the namespace for KEY."""
    vault_path = Path(vault)
    ns = get_namespace(vault_path, key)
    if ns is None:
        click.echo(f"No namespace set for '{key}'.")
    else:
        click.echo(ns)


@namespace_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str) -> None:
    """Remove the namespace assignment for KEY."""
    vault_path = Path(vault)
    remove_namespace(vault_path, key)
    click.echo(f"Namespace removed for '{key}'.")


@namespace_group.command("list")
@click.argument("vault")
def list_cmd(vault: str) -> None:
    """List all distinct namespaces in VAULT."""
    vault_path = Path(vault)
    namespaces = list_namespaces(vault_path)
    if not namespaces:
        click.echo("No namespaces defined.")
    else:
        for ns in namespaces:
            click.echo(ns)


@namespace_group.command("keys")
@click.argument("vault")
@click.argument("namespace")
def keys_cmd(vault: str, namespace: str) -> None:
    """List all keys in NAMESPACE."""
    vault_path = Path(vault)
    keys = keys_in_namespace(vault_path, namespace)
    if not keys:
        click.echo(f"No keys in namespace '{namespace}'.")
    else:
        for k in keys:
            click.echo(k)
