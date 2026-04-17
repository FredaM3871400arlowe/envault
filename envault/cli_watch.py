"""CLI commands for watching a .env file and auto-syncing into a vault."""
from __future__ import annotations

from pathlib import Path

import click

from envault.watch import watch_env_file


@click.group("watch")
def watch_group() -> None:
    """Watch a .env file and auto-sync changes into a vault."""


@watch_group.command("start")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("vault_file", type=click.Path(dir_okay=False))
@click.option("--password", "-p", prompt=True, hide_input=True, help="Vault password.")
@click.option("--interval", "-i", default=1.0, show_default=True, help="Poll interval in seconds.")
def start_cmd(env_file: str, vault_file: str, password: str, interval: float) -> None:
    """Watch ENV_FILE and merge changes into VAULT_FILE whenever it is modified."""
    env_path = Path(env_file)
    vault_path = Path(vault_file)

    click.echo(f"Watching {env_path} → {vault_path}  (interval={interval}s)  Ctrl-C to stop.")

    def _on_sync(vp: Path) -> None:
        click.echo(f"  [synced] {env_path.name} → {vp.name}")

    try:
        watch_env_file(env_path, vault_path, password, interval=interval, on_sync=_on_sync)
    except KeyboardInterrupt:
        click.echo("Stopped watching.")
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc
