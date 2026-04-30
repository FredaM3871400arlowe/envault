"""Tests for envault.cli_retention."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_retention import retention_group
from envault.vault import create_vault


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(tmp_path / "test.vault", "secret", {"API_KEY": "abc123"})


def test_set_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(retention_group, ["set", str(vault_path), "API_KEY", "30", "days"])
    assert result.exit_code == 0
    assert "Retention set" in result.output
    assert "API_KEY" in result.output


def test_set_invalid_unit_exits_nonzero(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(retention_group, ["set", str(vault_path), "API_KEY", "10", "minutes"])
    assert result.exit_code != 0


def test_set_zero_value_exits_nonzero(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(retention_group, ["set", str(vault_path), "API_KEY", "0", "days"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_get_existing_retention(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(retention_group, ["set", str(vault_path), "API_KEY", "2", "weeks"])
    result = runner.invoke(retention_group, ["get", str(vault_path), "API_KEY"])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "weeks" in result.output


def test_get_missing_key_shows_message(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(retention_group, ["get", str(vault_path), "GHOST"])
    assert result.exit_code == 0
    assert "No retention policy" in result.output


def test_remove_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(retention_group, ["set", str(vault_path), "API_KEY", "30", "days"])
    result = runner.invoke(retention_group, ["remove", str(vault_path), "API_KEY"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_unknown_key_exits_nonzero(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(retention_group, ["remove", str(vault_path), "GHOST"])
    assert result.exit_code != 0


def test_list_expired_no_expired_shows_message(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(retention_group, ["set", str(vault_path), "API_KEY", "365", "days"])
    result = runner.invoke(retention_group, ["list-expired", str(vault_path)])
    assert result.exit_code == 0
    assert "No expired" in result.output
