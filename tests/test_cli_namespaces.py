"""CLI tests for envault namespace commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_namespaces import namespace_group
from envault.vault import create_vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path):
    return create_vault(tmp_path / "test.vault", "password")


def test_set_prints_confirmation(runner, vault_path):
    result = runner.invoke(namespace_group, ["set", str(vault_path), "DB_HOST", "database"])
    assert result.exit_code == 0
    assert "assigned to namespace 'database'" in result.output


def test_set_empty_namespace_exits_nonzero(runner, vault_path):
    result = runner.invoke(namespace_group, ["set", str(vault_path), "KEY", ""])
    assert result.exit_code != 0


def test_get_existing_namespace(runner, vault_path):
    runner.invoke(namespace_group, ["set", str(vault_path), "API_KEY", "secrets"])
    result = runner.invoke(namespace_group, ["get", str(vault_path), "API_KEY"])
    assert result.exit_code == 0
    assert "secrets" in result.output


def test_get_missing_namespace(runner, vault_path):
    result = runner.invoke(namespace_group, ["get", str(vault_path), "MISSING"])
    assert result.exit_code == 0
    assert "No namespace" in result.output


def test_remove_prints_confirmation(runner, vault_path):
    runner.invoke(namespace_group, ["set", str(vault_path), "DB_HOST", "database"])
    result = runner.invoke(namespace_group, ["remove", str(vault_path), "DB_HOST"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_list_shows_namespaces(runner, vault_path):
    runner.invoke(namespace_group, ["set", str(vault_path), "DB_HOST", "database"])
    runner.invoke(namespace_group, ["set", str(vault_path), "API_KEY", "secrets"])
    result = runner.invoke(namespace_group, ["list", str(vault_path)])
    assert result.exit_code == 0
    assert "database" in result.output
    assert "secrets" in result.output


def test_list_empty_vault(runner, vault_path):
    result = runner.invoke(namespace_group, ["list", str(vault_path)])
    assert result.exit_code == 0
    assert "No namespaces" in result.output


def test_keys_shows_keys_in_namespace(runner, vault_path):
    runner.invoke(namespace_group, ["set", str(vault_path), "DB_HOST", "database"])
    runner.invoke(namespace_group, ["set", str(vault_path), "DB_PORT", "database"])
    runner.invoke(namespace_group, ["set", str(vault_path), "API_KEY", "secrets"])
    result = runner.invoke(namespace_group, ["keys", str(vault_path), "database"])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "DB_PORT" in result.output
    assert "API_KEY" not in result.output


def test_keys_no_match_shows_message(runner, vault_path):
    result = runner.invoke(namespace_group, ["keys", str(vault_path), "nonexistent"])
    assert result.exit_code == 0
    assert "No keys" in result.output
