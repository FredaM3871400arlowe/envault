"""CLI tests for scope commands."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_scopes import scope_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path):
    return tmp_path / "my.vault"


def test_set_prints_confirmation(runner, vault_path):
    result = runner.invoke(scope_group, ["set", str(vault_path), "DB_URL", "prod"])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "DB_URL" in result.output


def test_set_invalid_scope_exits_nonzero(runner, vault_path):
    result = runner.invoke(scope_group, ["set", str(vault_path), "KEY", "unknown"])
    assert result.exit_code != 0


def test_get_existing_scope(runner, vault_path):
    runner.invoke(scope_group, ["set", str(vault_path), "API", "staging"])
    result = runner.invoke(scope_group, ["get", str(vault_path), "API"])
    assert result.exit_code == 0
    assert "staging" in result.output


def test_get_missing_scope_shows_message(runner, vault_path):
    result = runner.invoke(scope_group, ["get", str(vault_path), "MISSING"])
    assert result.exit_code == 0
    assert "No scope" in result.output


def test_remove_prints_confirmation(runner, vault_path):
    runner.invoke(scope_group, ["set", str(vault_path), "TOKEN", "dev"])
    result = runner.invoke(scope_group, ["remove", str(vault_path), "TOKEN"])
    assert result.exit_code == 0
    assert "removed" in result.output.lower()


def test_list_shows_all_scopes(runner, vault_path):
    runner.invoke(scope_group, ["set", str(vault_path), "A", "dev"])
    runner.invoke(scope_group, ["set", str(vault_path), "B", "prod"])
    result = runner.invoke(scope_group, ["list", str(vault_path)])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output


def test_list_filter_by_scope(runner, vault_path):
    runner.invoke(scope_group, ["set", str(vault_path), "X", "ci"])
    runner.invoke(scope_group, ["set", str(vault_path), "Y", "dev"])
    result = runner.invoke(scope_group, ["list", str(vault_path), "--scope", "ci"])
    assert result.exit_code == 0
    assert "X" in result.output
    assert "Y" not in result.output


def test_list_filter_invalid_scope_exits_nonzero(runner, vault_path):
    result = runner.invoke(scope_group, ["list", str(vault_path), "--scope", "fantasy"])
    assert result.exit_code != 0
