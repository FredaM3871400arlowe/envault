"""Integration tests for key classification CLI."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_classifications import classification_group
from envault.classifications import get_classification
from envault.vault import create_vault, update_vault


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(
        tmp_path / "test.vault",
        "pw",
        {"DB_PASSWORD": "secret123", "APP_URL": "https://example.com", "DEBUG": "false"},
    )


def test_set_then_list_shows_entry(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(classification_group, ["set", str(vault_path), "DB_PASSWORD", "secret"])
    result = runner.invoke(classification_group, ["list", str(vault_path)])
    assert "DB_PASSWORD" in result.output
    assert "secret" in result.output


def test_auto_then_get_returns_classification(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(classification_group, ["auto", str(vault_path)], input="pw\n")
    cls = get_classification(vault_path, "DB_PASSWORD")
    assert cls == "secret"


def test_remove_then_list_excludes_key(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(classification_group, ["set", str(vault_path), "APP_URL", "url"])
    runner.invoke(classification_group, ["remove", str(vault_path), "APP_URL"])
    result = runner.invoke(classification_group, ["list", str(vault_path)])
    assert "APP_URL" not in result.output


def test_manual_overrides_auto(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(classification_group, ["auto", str(vault_path)], input="pw\n")
    runner.invoke(classification_group, ["set", str(vault_path), "DB_PASSWORD", "config"])
    assert get_classification(vault_path, "DB_PASSWORD") == "config"
