"""Tests for envault.cli_expiry."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.vault import create_vault
from envault.expiry import set_expiry
from envault.cli_expiry import expiry_group

PASSWORD = "pw"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    return create_vault(tmp_path / "v.vault", PASSWORD, {"A": "1", "B": "2"})


def test_set_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(expiry_group, ["set", str(vault_path), "A", "2099-01-01T00:00:00"])
    assert result.exit_code == 0
    assert "Expiry set for 'A'" in result.output


def test_set_invalid_date_exits_nonzero(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(expiry_group, ["set", str(vault_path), "A", "not-a-date"])
    assert result.exit_code != 0


def test_show_existing_expiry(runner: CliRunner, vault_path: Path) -> None:
    future = datetime(2099, 6, 1, tzinfo=timezone.utc)
    set_expiry(vault_path, "A", future)
    result = runner.invoke(expiry_group, ["show", str(vault_path), "A"])
    assert result.exit_code == 0
    assert "A:" in result.output


def test_show_no_expiry(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(expiry_group, ["show", str(vault_path), "A"])
    assert "No expiry" in result.output


def test_clear_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(expiry_group, ["clear", str(vault_path), "A"])
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_list_expired_shows_keys(runner: CliRunner, vault_path: Path) -> None:
    past = datetime.now(timezone.utc) - timedelta(seconds=5)
    set_expiry(vault_path, "A", past)
    result = runner.invoke(expiry_group, ["list-expired", str(vault_path)])
    assert "A" in result.output


def test_purge_removes_expired(runner: CliRunner, vault_path: Path) -> None:
    past = datetime.now(timezone.utc) - timedelta(seconds=5)
    set_expiry(vault_path, "A", past)
    result = runner.invoke(expiry_group, ["purge", str(vault_path), "--password", PASSWORD])
    assert result.exit_code == 0
    assert "Purged" in result.output
    assert "A" in result.output
