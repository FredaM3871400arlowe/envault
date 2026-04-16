"""Tests for vault password rotation."""

import pytest
from pathlib import Path
from click.testing import CliRunner
from envault.vault import create_vault, read_vault
from envault.rotate import rotate_password
from envault.cli_rotate import rotate_group


@pytest.fixture
def vault_path(tmp_path):
    path = tmp_path / "test.vault"
    create_vault(path, "oldpass", initial_data={"KEY": "value", "FOO": "bar"})
    return path


def test_rotate_password_returns_path(vault_path):
    result = rotate_password(vault_path, "oldpass", "newpass")
    assert result == vault_path


def test_rotate_password_new_password_works(vault_path):
    rotate_password(vault_path, "oldpass", "newpass")
    data = read_vault(vault_path, "newpass")
    assert data["KEY"] == "value"
    assert data["FOO"] == "bar"


def test_rotate_password_old_password_no_longer_works(vault_path):
    rotate_password(vault_path, "oldpass", "newpass")
    with pytest.raises(ValueError):
        read_vault(vault_path, "oldpass")


def test_rotate_wrong_old_password_raises(vault_path):
    with pytest.raises(ValueError):
        rotate_password(vault_path, "wrongpass", "newpass")


def test_rotate_missing_vault_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        rotate_password(tmp_path / "missing.vault", "oldpass", "newpass")


# --- CLI tests ---

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_rotate_success(runner, vault_path):
    result = runner.invoke(
        rotate_group,
        ["password", str(vault_path), "--old-password", "oldpass", "--new-password", "newpass"],
    )
    assert result.exit_code == 0
    assert "rotated successfully" in result.output


def test_cli_rotate_same_password_error(runner, vault_path):
    result = runner.invoke(
        rotate_group,
        ["password", str(vault_path), "--old-password", "oldpass", "--new-password", "oldpass"],
    )
    assert result.exit_code != 0
    assert "must differ" in result.output


def test_cli_rotate_wrong_old_password(runner, vault_path):
    result = runner.invoke(
        rotate_group,
        ["password", str(vault_path), "--old-password", "wrong", "--new-password", "newpass"],
    )
    assert result.exit_code != 0
    assert "incorrect old password" in result.output
