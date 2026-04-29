"""CLI commands for managing key quotas per namespace."""

from __future__ import annotations

from pathlib import Path

import click

from .quotas import (
    check_quota,
    get_quota,
    list_quotas,
    remove_quota,
    set_quota,
)


@click.group("quotas")
def quotas_group() -> None:
    """Manage key quotas per namespace."""


@quotas_group.command("set")
@click.argument("vault")
@click.argument("namespace")
@click.argument("limit", type=int)
def set_cmd(vault: str, namespace: str, limit: int) -> None:
    """Set the quota LIMIT for NAMESPACE in VAULT."""
    vault_path = Path(vault)
    try:
        set_quota(vault_path, namespace, limit)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Quota for '{namespace}' set to {limit} keys.")


@quotas_group.command("get")
@click.argument("vault")
@click.argument("namespace")
def get_cmd(vault: str, namespace: str) -> None:
    """Show the quota for NAMESPACE in VAULT."""
    limit = get_quota(Path(vault), namespace)
    if limit is None:
        click.echo(f"No quota set for '{namespace}'.")
    else:
        click.echo(f"{namespace}: {limit} keys")


@quotas_group.command("remove")
@click.argument("vault")
@click.argument("namespace")
def remove_cmd(vault: str, namespace: str) -> None:
    """Remove the quota for NAMESPACE in VAULT."""
    remove_quota(Path(vault), namespace)
    click.echo(f"Quota for '{namespace}' removed.")


@quotas_group.command("list")
@click.argument("vault")
def list_cmd(vault: str) -> None:
    """List all quotas configured for VAULT."""
    quotas = list_quotas(Path(vault))
    if not quotas:
        click.echo("No quotas configured.")
        return
    for ns, limit in sorted(quotas.items()):
        click.echo(f"  {ns}: {limit} keys")


@quotas_group.command("check")
@click.argument("vault")
@click.argument("namespace")
@click.argument("count", type=int)
def check_cmd(vault: str, namespace: str, count: int) -> None:
    """Check whether COUNT keys is within the quota for NAMESPACE."""
    within = check_quota(Path(vault), namespace, count)
    if within:
        click.echo(f"OK — {count} keys is within the quota for '{namespace}'.")
    else:
        raise click.ClickException(
            f"Quota exceeded for '{namespace}': {count} keys at or above limit."
        )
