"""Tests for envault.cli_lifecycle."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_lifecycle import lifecycle_group
from envault.vault import create_vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path):
    p = create_vault(str(tmp_path / "test.vault"), "password")
    return str(p)


def test_set_prints_confirmation(runner, vault_path):
    result = runner.invoke(lifecycle_group, ["set", vault_path, "MY_KEY", "draft"])
    assert result.exit_code == 0
    assert "draft" in result.output


def test_set_invalid_state_exits_nonzero(runner, vault_path):
    result = runner.invoke(lifecycle_group, ["set", vault_path, "MY_KEY", "bogus"])
    assert result.exit_code != 0


def test_set_invalid_transition_exits_nonzero(runner, vault_path):
    runner.invoke(lifecycle_group, ["set", vault_path, "K", "draft"])
    result = runner.invoke(lifecycle_group, ["set", vault_path, "K", "archived"])
    assert result.exit_code != 0
    assert "Cannot transition" in result.output


def test_get_existing_state(runner, vault_path):
    runner.invoke(lifecycle_group, ["set", vault_path, "K", "draft"])
    result = runner.invoke(lifecycle_group, ["get", vault_path, "K"])
    assert result.exit_code == 0
    assert "draft" in result.output


def test_get_missing_state(runner, vault_path):
    result = runner.invoke(lifecycle_group, ["get", vault_path, "MISSING"])
    assert result.exit_code == 0
    assert "No lifecycle state" in result.output


def test_remove_prints_confirmation(runner, vault_path):
    runner.invoke(lifecycle_group, ["set", vault_path, "K", "draft"])
    result = runner.invoke(lifecycle_group, ["remove", vault_path, "K"])
    assert result.exit_code == 0
    assert "removed" in result.output.lower()


def test_list_shows_matching_keys(runner, vault_path):
    runner.invoke(lifecycle_group, ["set", vault_path, "A", "draft"])
    runner.invoke(lifecycle_group, ["set", vault_path, "B", "draft"])
    runner.invoke(lifecycle_group, ["set", vault_path, "B", "active"])
    result = runner.invoke(lifecycle_group, ["list", vault_path, "draft"])
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" not in result.output


def test_list_no_matches(runner, vault_path):
    result = runner.invoke(lifecycle_group, ["list", vault_path, "archived"])
    assert result.exit_code == 0
    assert "No keys" in result.output
