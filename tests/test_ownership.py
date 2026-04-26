"""Tests for envault.ownership."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.ownership import (
    _ownership_path,
    get_owner,
    list_by_owner,
    load_ownership,
    remove_owner,
    set_owner,
)
from envault.cli_ownership import ownership_group


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "test.vault"


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_ownership_path_is_sibling_of_vault(vault_path: Path) -> None:
    p = _ownership_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.ownership.json"


def test_load_ownership_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_ownership(vault_path) == {}


def test_set_and_get_owner(vault_path: Path) -> None:
    set_owner(vault_path, "DB_PASSWORD", "alice")
    assert get_owner(vault_path, "DB_PASSWORD") == "alice"


def test_get_owner_missing_key_returns_none(vault_path: Path) -> None:
    assert get_owner(vault_path, "NONEXISTENT") is None


def test_set_owner_empty_key_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="key"):
        set_owner(vault_path, "", "alice")


def test_set_owner_empty_owner_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="owner"):
        set_owner(vault_path, "API_KEY", "")


def test_remove_owner_removes_entry(vault_path: Path) -> None:
    set_owner(vault_path, "SECRET", "bob")
    remove_owner(vault_path, "SECRET")
    assert get_owner(vault_path, "SECRET") is None


def test_remove_owner_missing_key_is_noop(vault_path: Path) -> None:
    remove_owner(vault_path, "GHOST")  # should not raise


def test_list_by_owner_returns_correct_keys(vault_path: Path) -> None:
    set_owner(vault_path, "DB_HOST", "alice")
    set_owner(vault_path, "DB_PASS", "alice")
    set_owner(vault_path, "API_KEY", "bob")
    keys = list_by_owner(vault_path, "alice")
    assert set(keys) == {"DB_HOST", "DB_PASS"}


def test_list_by_owner_unknown_returns_empty(vault_path: Path) -> None:
    assert list_by_owner(vault_path, "nobody") == []


# CLI tests

def test_cli_set_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(ownership_group, ["set", str(vault_path), "MY_KEY", "carol"])
    assert result.exit_code == 0
    assert "carol" in result.output


def test_cli_get_existing_owner(runner: CliRunner, vault_path: Path) -> None:
    set_owner(vault_path, "MY_KEY", "dave")
    result = runner.invoke(ownership_group, ["get", str(vault_path), "MY_KEY"])
    assert result.exit_code == 0
    assert "dave" in result.output


def test_cli_get_missing_key(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(ownership_group, ["get", str(vault_path), "MISSING"])
    assert result.exit_code == 0
    assert "No owner" in result.output


def test_cli_list_filter_by_owner(runner: CliRunner, vault_path: Path) -> None:
    set_owner(vault_path, "K1", "eve")
    set_owner(vault_path, "K2", "frank")
    result = runner.invoke(ownership_group, ["list", str(vault_path), "--owner", "eve"])
    assert result.exit_code == 0
    assert "K1" in result.output
    assert "K2" not in result.output
