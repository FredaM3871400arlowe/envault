"""CLI tests for the alias commands."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_aliases import alias_group
from envault.vault import create_vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    create_vault(str(p), "password", {"DATABASE_URL": "postgres://localhost/db"})
    return str(p)


def test_add_prints_confirmation(runner, vault_path):
    result = runner.invoke(alias_group, ["add", "db", "DATABASE_URL", "--vault", vault_path])
    assert result.exit_code == 0
    assert "db" in result.output
    assert "DATABASE_URL" in result.output


def test_remove_prints_confirmation(runner, vault_path):
    runner.invoke(alias_group, ["add", "db", "DATABASE_URL", "--vault", vault_path])
    result = runner.invoke(alias_group, ["remove", "db", "--vault", vault_path])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_unknown_alias_shows_error(runner, vault_path):
    result = runner.invoke(alias_group, ["remove", "ghost", "--vault", vault_path])
    assert result.exit_code != 0


def test_list_shows_aliases(runner, vault_path):
    runner.invoke(alias_group, ["add", "db", "DATABASE_URL", "--vault", vault_path])
    result = runner.invoke(alias_group, ["list", "--vault", vault_path])
    assert result.exit_code == 0
    assert "db" in result.output
    assert "DATABASE_URL" in result.output


def test_list_empty_shows_message(runner, vault_path):
    result = runner.invoke(alias_group, ["list", "--vault", vault_path])
    assert result.exit_code == 0
    assert "No aliases" in result.output


def test_resolve_returns_mapped_key(runner, vault_path):
    runner.invoke(alias_group, ["add", "db", "DATABASE_URL", "--vault", vault_path])
    result = runner.invoke(alias_group, ["resolve", "db", "--vault", vault_path])
    assert result.exit_code == 0
    assert "DATABASE_URL" in result.output
