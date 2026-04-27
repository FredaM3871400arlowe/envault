"""CLI commands for managing key constraints."""

from __future__ import annotations

import click

from envault.constraints import (
    check_value,
    get_constraint,
    load_constraints,
    remove_constraint,
    set_constraint,
)
from envault.vault import read_vault


@click.group("constraints")
def constraints_group() -> None:
    """Attach and verify value constraints for vault keys."""


@constraints_group.command("set")
@click.argument("vault")
@click.argument("key")
@click.option("--pattern", default=None, help="Regex the value must fully match.")
@click.option("--min-length", type=int, default=None, help="Minimum value length.")
@click.option("--max-length", type=int, default=None, help="Maximum value length.")
@click.option(
    "--allowed",
    multiple=True,
    metavar="VALUE",
    help="Allowed value (repeat for multiple).",
)
def set_cmd(
    vault: str,
    key: str,
    pattern: str | None,
    min_length: int | None,
    max_length: int | None,
    allowed: tuple[str, ...],
) -> None:
    """Set a constraint on KEY in VAULT."""
    try:
        set_constraint(
            vault,
            key,
            pattern=pattern,
            min_length=min_length,
            max_length=max_length,
            allowed_values=list(allowed) if allowed else None,
        )
    except (ValueError, re.error) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Constraint set for '{key}'.")


@constraints_group.command("get")
@click.argument("vault")
@click.argument("key")
def get_cmd(vault: str, key: str) -> None:
    """Show the constraint for KEY."""
    constraint = get_constraint(vault, key)
    if constraint is None:
        click.echo(f"No constraint for '{key}'.")
    else:
        for field, val in constraint.items():
            click.echo(f"  {field}: {val}")


@constraints_group.command("remove")
@click.argument("vault")
@click.argument("key")
def remove_cmd(vault: str, key: str) -> None:
    """Remove the constraint for KEY."""
    if remove_constraint(vault, key):
        click.echo(f"Constraint removed for '{key}'.")
    else:
        raise click.ClickException(f"No constraint found for '{key}'.")


@constraints_group.command("list")
@click.argument("vault")
def list_cmd(vault: str) -> None:
    """List all keys that have constraints."""
    data = load_constraints(vault)
    if not data:
        click.echo("No constraints defined.")
    else:
        for key in sorted(data):
            click.echo(key)


@constraints_group.command("verify")
@click.argument("vault")
@click.argument("password")
@click.option("--key", default=None, help="Only verify this key.")
@click.pass_context
def verify_cmd(ctx: click.Context, vault: str, password: str, key: str | None) -> None:
    """Verify vault values against their constraints."""
    try:
        env = read_vault(vault, password)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    constraints = load_constraints(vault)
    keys_to_check = [key] if key else list(env.keys())
    failed = False
    for k in keys_to_check:
        if k not in constraints:
            continue
        value = env.get(k, "")
        violations = check_value(constraints[k], value)
        if violations:
            failed = True
            for msg in violations:
                click.echo(f"FAIL  {k}: {msg}")
        else:
            click.echo(f"OK    {k}")
    if failed:
        ctx.exit(1)


import re  # noqa: E402 (needed for re.error in set_cmd)
