"""Tests for envault.environments and envault.cli_environments."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.environments import (
    ENVIRONMENT_FILE,
    get_environment,
    list_by_environment,
    load_environments,
    remove_environment,
    set_environment,
)
from envault.cli_environments import environments_group
from envault.vault import create_vault

PASSWORD = "test-pass"


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(tmp_path / "test.vault", PASSWORD)


# --- unit tests ---

def test_environments_path_is_sibling_of_vault(vault_path: Path) -> None:
    from envault.environments import _environments_path
    p = _environments_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == ENVIRONMENT_FILE


def test_load_environments_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_environments(vault_path) == {}


def test_set_and_get_environment(vault_path: Path) -> None:
    set_environment(vault_path, "DB_URL", "prod")
    assert get_environment(vault_path, "DB_URL") == "prod"


def test_get_environment_missing_key_returns_none(vault_path: Path) -> None:
    assert get_environment(vault_path, "MISSING") is None


def test_set_invalid_environment_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid environment"):
        set_environment(vault_path, "KEY", "fantasy")


def test_remove_environment(vault_path: Path) -> None:
    set_environment(vault_path, "API_KEY", "staging")
    remove_environment(vault_path, "API_KEY")
    assert get_environment(vault_path, "API_KEY") is None


def test_list_by_environment(vault_path: Path) -> None:
    set_environment(vault_path, "DB_URL", "prod")
    set_environment(vault_path, "API_KEY", "prod")
    set_environment(vault_path, "DEBUG", "dev")
    result = list_by_environment(vault_path, "prod")
    assert result == ["API_KEY", "DB_URL"]


# --- CLI tests ---

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_set_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(environments_group, ["set", str(vault_path), "DB_URL", "dev"])
    assert result.exit_code == 0
    assert "dev" in result.output


def test_set_invalid_env_exits_nonzero(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(environments_group, ["set", str(vault_path), "KEY", "fantasy"])
    assert result.exit_code != 0


def test_get_existing_environment(runner: CliRunner, vault_path: Path) -> None:
    set_environment(vault_path, "SECRET", "staging")
    result = runner.invoke(environments_group, ["get", str(vault_path), "SECRET"])
    assert result.exit_code == 0
    assert "staging" in result.output


def test_get_missing_environment(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(environments_group, ["get", str(vault_path), "NOPE"])
    assert result.exit_code == 0
    assert "No environment" in result.output


def test_find_lists_keys(runner: CliRunner, vault_path: Path) -> None:
    set_environment(vault_path, "DB_URL", "prod")
    set_environment(vault_path, "CACHE_URL", "prod")
    result = runner.invoke(environments_group, ["find", str(vault_path), "prod"])
    assert "DB_URL" in result.output
    assert "CACHE_URL" in result.output


def test_find_invalid_env_exits_nonzero(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(environments_group, ["find", str(vault_path), "nowhere"])
    assert result.exit_code != 0
