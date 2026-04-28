"""CLI commands for vault key sentiment / confidence analysis."""

from __future__ import annotations

from pathlib import Path

import click

from envault.sentiment import analyse_sentiment, get_confidence, load_sentiment
from envault.vault import read_vault


@click.group("sentiment")
def sentiment_group() -> None:
    """Analyse confidence levels of vault key values."""


@sentiment_group.command("analyse")
@click.argument("vault")
@click.password_option("--password", "-p", prompt="Vault password", confirmation_prompt=False)
def analyse_cmd(vault: str, password: str) -> None:
    """Analyse all keys and print confidence scores."""
    vault_path = Path(vault)
    try:
        env = read_vault(vault_path, password)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    results = analyse_sentiment(vault_path, env)
    if not results:
        click.echo("No keys found in vault.")
        return

    for key, result in sorted(results.items()):
        colour = {"high": "green", "medium": "yellow", "low": "red"}.get(result.confidence, "white")
        badge = click.style(result.confidence.upper(), fg=colour, bold=True)
        click.echo(f"  {key}: {badge}")
        for reason in result.reasons:
            click.echo(f"    - {reason}")


@sentiment_group.command("show")
@click.argument("vault")
@click.argument("key")
def show_cmd(vault: str, key: str) -> None:
    """Show the stored confidence level for a single key."""
    vault_path = Path(vault)
    confidence = get_confidence(vault_path, key)
    if confidence is None:
        click.echo(f"No sentiment data for '{key}'. Run 'analyse' first.")
        raise SystemExit(1)
    colour = {"high": "green", "medium": "yellow", "low": "red"}.get(confidence, "white")
    click.echo(click.style(confidence.upper(), fg=colour, bold=True))


@sentiment_group.command("list")
@click.argument("vault")
@click.option("--level", type=click.Choice(["low", "medium", "high"]), default=None, help="Filter by confidence level.")
def list_cmd(vault: str, level: str | None) -> None:
    """List stored confidence scores, optionally filtered by level."""
    vault_path = Path(vault)
    data = load_sentiment(vault_path)
    if not data:
        click.echo("No sentiment data found. Run 'analyse' first.")
        return
    for key, confidence in sorted(data.items()):
        if level and confidence != level:
            continue
        colour = {"high": "green", "medium": "yellow", "low": "red"}.get(confidence, "white")
        click.echo(f"  {key}: {click.style(confidence, fg=colour)}")
