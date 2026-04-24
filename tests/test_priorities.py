"""Tests for envault.priorities."""
from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.vault import create_vault
from envault.priorities import (
    _priorities_path,
    load_priorities,
    set_priority,
    get_priority,
    remove_priority,
    list_by_priority,
)
from envault.cli_priorities import priorities_group


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(str(tmp_path / "test.vault"), "password", {})


def test_priorities_path_is_sibling_of_vault(vault_path: Path) -> None:
    p = _priorities_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.priorities.json"


def test_load_priorities_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_priorities(vault_path) == {}


def test_set_and_get_priority(vault_path: Path) -> None:
    set_priority(vault_path, "DB_PASSWORD", "critical")
    assert get_priority(vault_path, "DB_PASSWORD") == "critical"


def test_get_priority_missing_key_returns_none(vault_path: Path) -> None:
    assert get_priority(vault_path, "MISSING") is None


def test_set_priority_invalid_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid priority"):
        set_priority(vault_path, "KEY", "urgent")


def test_set_priority_case_insensitive(vault_path: Path) -> None:
    set_priority(vault_path, "API_KEY", "HIGH")
    assert get_priority(vault_path, "API_KEY") == "high"


def test_remove_priority_returns_true(vault_path: Path) -> None:
    set_priority(vault_path, "KEY", "low")
    assert remove_priority(vault_path, "KEY") is True
    assert get_priority(vault_path, "KEY") is None


def test_remove_priority_missing_returns_false(vault_path: Path) -> None:
    assert remove_priority(vault_path, "GHOST") is False


def test_list_by_priority_returns_matching_keys(vault_path: Path) -> None:
    set_priority(vault_path, "A", "high")
    set_priority(vault_path, "B", "low")
    set_priority(vault_path, "C", "high")
    result = list_by_priority(vault_path, "high")
    assert result == ["A", "C"]


def test_list_by_priority_invalid_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError):
        list_by_priority(vault_path, "extreme")


# --- CLI tests ---

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_set_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(priorities_group, ["set", str(vault_path), "MY_KEY", "medium"])
    assert result.exit_code == 0
    assert "medium" in result.output


def test_get_existing_priority(runner: CliRunner, vault_path: Path) -> None:
    set_priority(vault_path, "MY_KEY", "critical")
    result = runner.invoke(priorities_group, ["get", str(vault_path), "MY_KEY"])
    assert result.exit_code == 0
    assert "critical" in result.output


def test_get_missing_priority_shows_message(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(priorities_group, ["get", str(vault_path), "GHOST"])
    assert result.exit_code == 0
    assert "No priority" in result.output


def test_remove_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    set_priority(vault_path, "X", "low")
    result = runner.invoke(priorities_group, ["remove", str(vault_path), "X"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_unknown_shows_error(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(priorities_group, ["remove", str(vault_path), "GHOST"])
    assert result.exit_code != 0


def test_list_shows_all_priorities(runner: CliRunner, vault_path: Path) -> None:
    set_priority(vault_path, "A", "high")
    set_priority(vault_path, "B", "low")
    result = runner.invoke(priorities_group, ["list", str(vault_path)])
    assert result.exit_code == 0
    assert "A: high" in result.output
    assert "B: low" in result.output


def test_list_filter_by_priority(runner: CliRunner, vault_path: Path) -> None:
    set_priority(vault_path, "A", "high")
    set_priority(vault_path, "B", "low")
    result = runner.invoke(priorities_group, ["list", str(vault_path), "--filter", "high"])
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" not in result.output
