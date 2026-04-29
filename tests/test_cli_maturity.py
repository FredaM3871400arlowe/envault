"""Tests for envault.cli_maturity."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_maturity import maturity_group
from envault.vault import create_vault


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    p = tmp_path / "env.vault"
    create_vault(p, {"DB_URL": "postgres://localhost", "API_KEY": "abc123"}, "pass")
    return p


def test_analyse_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(
        maturity_group, ["analyse", str(vault_path), "--password", "pass"]
    )
    assert result.exit_code == 0
    assert "Analysed 2 key(s)" in result.output


def test_analyse_wrong_password_exits_nonzero(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(
        maturity_group, ["analyse", str(vault_path), "--password", "wrong"]
    )
    assert result.exit_code != 0


def test_show_after_analyse(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(maturity_group, ["analyse", str(vault_path), "--password", "pass"])
    result = runner.invoke(maturity_group, ["show", str(vault_path), "DB_URL"])
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "Level" in result.output


def test_show_missing_key_before_analyse(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(maturity_group, ["show", str(vault_path), "UNKNOWN"])
    assert result.exit_code == 0
    assert "No maturity data" in result.output


def test_list_shows_all_keys(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(maturity_group, ["analyse", str(vault_path), "--password", "pass"])
    result = runner.invoke(maturity_group, ["list", str(vault_path)])
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "API_KEY" in result.output


def test_list_filter_by_level(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(maturity_group, ["analyse", str(vault_path), "--password", "pass"])
    result = runner.invoke(maturity_group, ["list", str(vault_path), "--level", "new"])
    assert result.exit_code == 0
    # freshly created vault keys are all 'new'
    assert "new" in result.output


def test_list_no_data_shows_message(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(maturity_group, ["list", str(vault_path)])
    assert result.exit_code == 0
    assert "No maturity data" in result.output
