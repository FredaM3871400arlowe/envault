"""Tests for envault/cli_reactions.py"""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_reactions import reactions_group
from envault.vault import create_vault


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(tmp_path / "test.vault", "password", {"API_KEY": "abc123"})


def test_add_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(reactions_group, ["add", str(vault_path), "API_KEY", "👍"])
    assert result.exit_code == 0
    assert "👍" in result.output
    assert "API_KEY" in result.output


def test_add_invalid_reaction_exits_nonzero(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(reactions_group, ["add", str(vault_path), "API_KEY", "💩"])
    assert result.exit_code != 0


def test_remove_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(reactions_group, ["add", str(vault_path), "API_KEY", "👍"])
    runner.invoke(reactions_group, ["add", str(vault_path), "API_KEY", "🔥"])
    result = runner.invoke(reactions_group, ["remove", str(vault_path), "API_KEY", "👍"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_show_existing_reactions(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(reactions_group, ["add", str(vault_path), "API_KEY", "✅"])
    result = runner.invoke(reactions_group, ["show", str(vault_path), "API_KEY"])
    assert result.exit_code == 0
    assert "✅" in result.output


def test_show_no_reactions(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(reactions_group, ["show", str(vault_path), "API_KEY"])
    assert result.exit_code == 0
    assert "No reactions" in result.output


def test_list_shows_all_keys(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(reactions_group, ["add", str(vault_path), "API_KEY", "👍"])
    runner.invoke(reactions_group, ["add", str(vault_path), "DB_URL", "🔥"])
    result = runner.invoke(reactions_group, ["list", str(vault_path)])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "DB_URL" in result.output


def test_list_empty_vault(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(reactions_group, ["list", str(vault_path)])
    assert result.exit_code == 0
    assert "No reactions" in result.output


def test_clear_removes_all(runner: CliRunner, vault_path: Path) -> None:
    runner.invoke(reactions_group, ["add", str(vault_path), "API_KEY", "👍"])
    runner.invoke(reactions_group, ["add", str(vault_path), "API_KEY", "🔥"])
    result = runner.invoke(reactions_group, ["clear", str(vault_path), "API_KEY"])
    assert result.exit_code == 0
    assert "cleared" in result.output
    show = runner.invoke(reactions_group, ["show", str(vault_path), "API_KEY"])
    assert "No reactions" in show.output
