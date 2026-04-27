"""Tests for envault/cli_constraints.py."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_constraints import constraints_group
from envault.vault import create_vault, update_vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    create_vault(str(p), "secret", {"PORT": "8080", "ENV": "dev"})
    return str(p)


def test_set_prints_confirmation(runner, vault_path):
    result = runner.invoke(
        constraints_group, ["set", vault_path, "PORT", "--min-length", "1"]
    )
    assert result.exit_code == 0
    assert "Constraint set" in result.output


def test_set_invalid_pattern_exits_nonzero(runner, vault_path):
    result = runner.invoke(
        constraints_group, ["set", vault_path, "KEY", "--pattern", "[bad"]
    )
    assert result.exit_code != 0


def test_get_existing_constraint(runner, vault_path):
    runner.invoke(
        constraints_group,
        ["set", vault_path, "PORT", "--min-length", "2", "--max-length", "10"],
    )
    result = runner.invoke(constraints_group, ["get", vault_path, "PORT"])
    assert result.exit_code == 0
    assert "min_length" in result.output


def test_get_missing_constraint(runner, vault_path):
    result = runner.invoke(constraints_group, ["get", vault_path, "MISSING"])
    assert result.exit_code == 0
    assert "No constraint" in result.output


def test_remove_prints_confirmation(runner, vault_path):
    runner.invoke(constraints_group, ["set", vault_path, "PORT", "--min-length", "1"])
    result = runner.invoke(constraints_group, ["remove", vault_path, "PORT"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_unknown_exits_nonzero(runner, vault_path):
    result = runner.invoke(constraints_group, ["remove", vault_path, "NOPE"])
    assert result.exit_code != 0


def test_list_shows_constrained_keys(runner, vault_path):
    runner.invoke(constraints_group, ["set", vault_path, "PORT", "--min-length", "1"])
    runner.invoke(
        constraints_group,
        ["set", vault_path, "ENV", "--allowed", "dev", "--allowed", "prod"],
    )
    result = runner.invoke(constraints_group, ["list", vault_path])
    assert "PORT" in result.output
    assert "ENV" in result.output


def test_verify_passes_for_valid_values(runner, vault_path):
    runner.invoke(
        constraints_group,
        ["set", vault_path, "PORT", "--pattern", r"\d+"],
    )
    result = runner.invoke(constraints_group, ["verify", vault_path, "secret"])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_verify_fails_for_invalid_values(runner, vault_path):
    runner.invoke(
        constraints_group,
        ["set", vault_path, "ENV", "--allowed", "production"],
    )
    result = runner.invoke(constraints_group, ["verify", vault_path, "secret"])
    assert result.exit_code != 0
    assert "FAIL" in result.output


def test_verify_wrong_password_exits_nonzero(runner, vault_path):
    result = runner.invoke(constraints_group, ["verify", vault_path, "wrong"])
    assert result.exit_code != 0
