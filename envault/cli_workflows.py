"""CLI commands for managing envault workflows."""
from __future__ import annotations

import subprocess
import sys

import click

from .workflows import (
    add_workflow,
    get_workflow,
    list_workflows,
    remove_workflow,
)


@click.group("workflow")
def workflow_group() -> None:
    """Manage named workflows (sequences of steps) for a vault."""


@workflow_group.command("add")
@click.argument("vault")
@click.argument("name")
@click.option("--step", "steps", multiple=True, required=True, help="Step command (repeatable).")
@click.option("--description", default="", help="Optional description.")
def add_cmd(vault: str, name: str, steps: tuple[str, ...], description: str) -> None:
    """Add or overwrite a workflow NAME on VAULT."""
    try:
        add_workflow(vault, name, list(steps), description)
        click.echo(f"Workflow '{name}' saved with {len(steps)} step(s).")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@workflow_group.command("remove")
@click.argument("vault")
@click.argument("name")
def remove_cmd(vault: str, name: str) -> None:
    """Remove workflow NAME from VAULT."""
    try:
        remove_workflow(vault, name)
        click.echo(f"Workflow '{name}' removed.")
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@workflow_group.command("list")
@click.argument("vault")
def list_cmd(vault: str) -> None:
    """List all workflows defined for VAULT."""
    names = list_workflows(vault)
    if not names:
        click.echo("No workflows defined.")
    for name in names:
        click.echo(name)


@workflow_group.command("show")
@click.argument("vault")
@click.argument("name")
def show_cmd(vault: str, name: str) -> None:
    """Show details of workflow NAME."""
    wf = get_workflow(vault, name)
    if wf is None:
        click.echo(f"Workflow '{name}' not found.", err=True)
        sys.exit(1)
    if wf["description"]:
        click.echo(f"Description: {wf['description']}")
    for i, step in enumerate(wf["steps"], 1):
        click.echo(f"  {i}. {step}")


@workflow_group.command("run")
@click.argument("vault")
@click.argument("name")
def run_cmd(vault: str, name: str) -> None:
    """Execute all steps of workflow NAME sequentially."""
    wf = get_workflow(vault, name)
    if wf is None:
        click.echo(f"Workflow '{name}' not found.", err=True)
        sys.exit(1)
    for step in wf["steps"]:
        click.echo(f"Running: {step}")
        result = subprocess.run(step, shell=True)
        if result.returncode != 0:
            click.echo(f"Step failed (exit {result.returncode}): {step}", err=True)
            sys.exit(result.returncode)
    click.echo(f"Workflow '{name}' completed successfully.")
