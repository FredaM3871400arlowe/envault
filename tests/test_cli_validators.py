"""Tests for envault.cli_validators."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.vault import create_vault, update_vault
from envault.cli_validators import validate_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    create_vault(str(p), "password")
    update_vault(str(p), "password", {"API_KEY": "abc123", "DB_URL": "postgres://x"})
    return str(p)


def test_run_clean_vault(runner, vault_path):
    result = runner.invoke(validate_group, ["run", vault_path, "-p", "password"])
    assert result.exit_code == 0
    assert "passed" in result.output


def test_run_vault_with_issues(runner, tmp_path):
    p = tmp_path / "bad.vault"
    create_vault(str(p), "password")
    update_vault(str(p), "password", {"bad_key": ""})
    result = runner.invoke(validate_group, ["run", str(p), "-p", "password"])
    assert result.exit_code == 0
    assert "Validation issues" in result.output


def test_run_strict_exits_nonzero(runner, tmp_path):
    p = tmp_path / "bad.vault"
    create_vault(str(p), "password")
    update_vault(str(p), "password", {"bad_key": ""})
    result = runner.invoke(validate_group, ["run", str(p), "-p", "password", "--strict"])
    assert result.exit_code != 0


def test_run_wrong_password_exits_nonzero(runner, vault_path):
    result = runner.invoke(validate_group, ["run", vault_path, "-p", "wrong"])
    assert result.exit_code != 0


def test_check_key_valid(runner, vault_path):
    result = runner.invoke(validate_group, ["check-key", vault_path, "API_KEY", "-p", "password"])
    assert result.exit_code == 0
    assert "passed" in result.output


def test_check_key_missing(runner, vault_path):
    result = runner.invoke(validate_group, ["check-key", vault_path, "MISSING_KEY", "-p", "password"])
    assert result.exit_code != 0
    assert "not found" in result.output
