"""CLI commands for value complexity scoring."""
from __future__ import annotations

from pathlib import Path

import click

from envault.complexity import compute_complexity, get_complexity


@click.group("complexity")
def complexity_group() -> None:
    """Analyse the complexity of vault key values."""


@complexity_group.command("analyse")
@click.argument("vault")
@click.password_option("--password", "-p", prompt="Vault password")
def analyse_cmd(vault: str, password: str) -> None:
    """Score the complexity of every value in the vault."""
    vault_path = Path(vault)
    try:
        results = compute_complexity(vault_path, password)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    if not results:
        click.echo("Vault is empty.")
        return

    click.echo(f"{'KEY':<30} {'SCORE':>5}  {'GRADE':>5}")
    click.echo("-" * 44)
    for r in sorted(results, key=lambda x: x.score):
        click.echo(f"{r.key:<30} {r.score:>5}  {r.grade:>5}")
        for reason in r.reasons:
            click.echo(f"  ⚠  {reason}")


@complexity_group.command("show")
@click.argument("vault")
@click.argument("key")
def show_cmd(vault: str, key: str) -> None:
    """Show the cached complexity score for a single key."""
    vault_path = Path(vault)
    result = get_complexity(vault_path, key)
    if result is None:
        raise click.ClickException(
            f"No complexity data for '{key}'. Run 'analyse' first."
        )
    click.echo(f"Key   : {result.key}")
    click.echo(f"Score : {result.score}/100")
    click.echo(f"Grade : {result.grade}")
    if result.reasons:
        click.echo("Issues:")
        for r in result.reasons:
            click.echo(f"  - {r}")
    else:
        click.echo("No issues found.")


@complexity_group.command("top")
@click.argument("vault")
@click.option("--n", default=5, show_default=True, help="Number of results to show.")
@click.option(
    "--worst", is_flag=True, default=False, help="Show weakest keys instead."
)
def top_cmd(vault: str, n: int, worst: bool) -> None:
    """Show the top (or worst) N keys by complexity score."""
    from envault.complexity import load_complexity

    vault_path = Path(vault)
    data = load_complexity(vault_path)
    if not data:
        raise click.ClickException("No complexity data found. Run 'analyse' first.")

    items = sorted(data.items(), key=lambda kv: kv[1]["score"], reverse=not worst)
    label = "Weakest" if worst else "Strongest"
    click.echo(f"{label} {n} keys:")
    for key, entry in items[:n]:
        click.echo(f"  {key}: {entry['score']}/100 ({entry['grade']})")
