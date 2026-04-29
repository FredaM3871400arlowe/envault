"""Tests for envault.cli_classifications."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_classifications import classification_group
from envault.classifications import set_classification
from envault.vault import create_vault


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(tmp_path / "test.vault", "pw", {"SECRET_KEY": "abc123"})


def test_set_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(classification_group, ["set", str(vault_path), "SECRET_KEY", "secret"])
    assert result.exit_code == 0
    assert "secret" in result.output


def test_set_invalid_classification_exits_nonzero(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(classification_group, ["set", str(vault_path), "SECRET_KEY", "banana"])
    assert result.exit_code != 0


def test_get_existing_classification(runner: CliRunner, vault_path: Path) -> None:
    set_classification(vault_path, "SECRET_KEY", "credential")
    result = runner.invoke(classification_group, ["get", str(vault_path), "SECRET_KEY"])
    assert result.exit_code == 0
    assert "credential" in result.output


def test_get_missing_key_shows_message(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(classification_group, ["get", str(vault_path), "GHOST"])
    assert result.exit_code == 0
    assert "No classification" in result.output


def test_remove_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    set_classification(vault_path, "SECRET_KEY", "secret")
    result = runner.invoke(classification_group, ["remove", str(vault_path), "SECRET_KEY"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_list_shows_entries(runner: CliRunner, vault_path: Path) -> None:
    set_classification(vault_path, "SECRET_KEY", "token")
    result = runner.invoke(classification_group, ["list", str(vault_path)])
    assert result.exit_code == 0
    assert "SECRET_KEY" in result.output
    assert "token" in result.output


def test_list_empty_shows_message(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(classification_group, ["list", str(vault_path)])
    assert result.exit_code == 0
    assert "No classifications" in result.output


def test_auto_classifies_vault_keys(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(
        classification_group,
        ["auto", str(vault_path)],
        input="pw\n",
    )
    assert result.exit_code == 0
    assert "Auto-classified" in result.output
