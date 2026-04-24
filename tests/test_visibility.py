"""Tests for envault.visibility and envault.cli_visibility."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.vault import create_vault
from envault.visibility import (
    _visibility_path,
    get_visibility,
    list_by_level,
    load_visibility,
    remove_visibility,
    set_visibility,
)
from envault.cli_visibility import visibility_group


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(str(tmp_path / "test.vault"), "secret", {"KEY1": "val1", "KEY2": "val2"})


# --- unit tests ---

def test_visibility_path_is_sibling_of_vault(vault_path: Path) -> None:
    vp = _visibility_path(vault_path)
    assert vp.parent == vault_path.parent
    assert vp.name == "test.visibility.json"


def test_load_visibility_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_visibility(vault_path) == {}


def test_set_and_get_visibility(vault_path: Path) -> None:
    set_visibility(vault_path, "KEY1", "private")
    assert get_visibility(vault_path, "KEY1") == "private"


def test_get_visibility_missing_key_returns_none(vault_path: Path) -> None:
    assert get_visibility(vault_path, "MISSING") is None


def test_set_invalid_level_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid visibility level"):
        set_visibility(vault_path, "KEY1", "secret")


def test_remove_visibility_returns_true_when_exists(vault_path: Path) -> None:
    set_visibility(vault_path, "KEY1", "public")
    assert remove_visibility(vault_path, "KEY1") is True
    assert get_visibility(vault_path, "KEY1") is None


def test_remove_visibility_returns_false_when_missing(vault_path: Path) -> None:
    assert remove_visibility(vault_path, "NOPE") is False


def test_list_by_level(vault_path: Path) -> None:
    set_visibility(vault_path, "KEY1", "public")
    set_visibility(vault_path, "KEY2", "private")
    assert list_by_level(vault_path, "public") == ["KEY1"]
    assert list_by_level(vault_path, "private") == ["KEY2"]


def test_list_by_invalid_level_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError):
        list_by_level(vault_path, "ghost")


# --- CLI tests ---

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_cli_set_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(visibility_group, ["set", str(vault_path), "KEY1", "private"])
    assert result.exit_code == 0
    assert "private" in result.output


def test_cli_get_existing(runner: CliRunner, vault_path: Path) -> None:
    set_visibility(vault_path, "KEY1", "restricted")
    result = runner.invoke(visibility_group, ["get", str(vault_path), "KEY1"])
    assert result.exit_code == 0
    assert "restricted" in result.output


def test_cli_get_missing(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(visibility_group, ["get", str(vault_path), "GHOST"])
    assert result.exit_code == 0
    assert "No visibility" in result.output


def test_cli_remove_unknown_exits_nonzero(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(visibility_group, ["remove", str(vault_path), "GHOST"])
    assert result.exit_code != 0


def test_cli_list_filtered_by_level(runner: CliRunner, vault_path: Path) -> None:
    set_visibility(vault_path, "KEY1", "public")
    set_visibility(vault_path, "KEY2", "private")
    result = runner.invoke(visibility_group, ["list", str(vault_path), "--level", "public"])
    assert result.exit_code == 0
    assert "KEY1" in result.output
    assert "KEY2" not in result.output
