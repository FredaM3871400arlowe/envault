"""Integration tests for maturity — analyse then inspect."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import json
import pytest
from click.testing import CliRunner

from envault.cli_maturity import maturity_group
from envault.maturity import _maturity_path
from envault.vault import create_vault
from envault.history import _history_path


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    p = tmp_path / "proj.vault"
    create_vault(p, {"SECRET": "s3cr3t", "TOKEN": "tok"}, "pw")
    return p


def _write_history(vault_path: Path, key: str, n_changes: int, oldest_days: float) -> None:
    """Inject synthetic history to drive maturity classification."""
    hp = _history_path(vault_path)
    existing: dict = json.loads(hp.read_text()) if hp.exists() else {}
    now = datetime.now(timezone.utc)
    entries = [
        {"timestamp": (now - timedelta(days=oldest_days - i * (oldest_days / max(n_changes, 1)))).isoformat(),
         "value": f"v{i}"}
        for i in range(n_changes)
    ]
    existing[key] = entries
    hp.write_text(json.dumps(existing, indent=2))


def test_analyse_then_list_shows_entries(runner: CliRunner, vault_path: Path) -> None:
    r = runner.invoke(maturity_group, ["analyse", str(vault_path), "--password", "pw"])
    assert r.exit_code == 0
    r2 = runner.invoke(maturity_group, ["list", str(vault_path)])
    assert "SECRET" in r2.output
    assert "TOKEN" in r2.output


def test_stale_key_classified_correctly(runner: CliRunner, vault_path: Path) -> None:
    _write_history(vault_path, "SECRET", 1, 100)
    runner.invoke(maturity_group, ["analyse", str(vault_path), "--password", "pw"])
    r = runner.invoke(maturity_group, ["show", str(vault_path), "SECRET"])
    assert "stale" in r.output


def test_mature_key_classified_correctly(runner: CliRunner, vault_path: Path) -> None:
    _write_history(vault_path, "TOKEN", 12, 45)
    runner.invoke(maturity_group, ["analyse", str(vault_path), "--password", "pw"])
    r = runner.invoke(maturity_group, ["show", str(vault_path), "TOKEN"])
    assert "mature" in r.output


def test_maturity_file_created_after_analyse(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(maturity_group, ["analyse", str(vault_path), "--password", "pw"])
    assert _maturity_path(vault_path).exists()
