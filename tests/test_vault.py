"""Tests for envault.vault module."""

import pytest
from pathlib import Path

from envault.vault import create_vault, read_vault, update_vault, delete_key

PASSWORD = "super-secret-123"


@pytest.fixture()
def tmp_vault(tmp_path):
    """Return a path string inside a temp directory (no file created yet)."""
    return str(tmp_path / "test")


def test_create_vault_returns_path(tmp_vault):
    path = create_vault(tmp_vault, PASSWORD, {"KEY": "value"})
    assert isinstance(path, Path)
    assert path.exists()
    assert path.suffix == ".vault"


def test_create_vault_adds_extension_if_missing(tmp_vault):
    path = create_vault(tmp_vault, PASSWORD, {})
    assert path.name.endswith(".vault")


def test_read_vault_roundtrip(tmp_vault):
    env_vars = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    create_vault(tmp_vault, PASSWORD, env_vars)
    result = read_vault(tmp_vault, PASSWORD)
    assert result == env_vars


def test_read_vault_wrong_password_raises(tmp_vault):
    create_vault(tmp_vault, PASSWORD, {"A": "1"})
    with pytest.raises(ValueError):
        read_vault(tmp_vault, "wrong-password")


def test_read_vault_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_vault(str(tmp_path / "nonexistent"), PASSWORD)


def test_update_vault_merges_keys(tmp_vault):
    create_vault(tmp_vault, PASSWORD, {"A": "1", "B": "2"})
    result = update_vault(tmp_vault, PASSWORD, {"B": "99", "C": "3"})
    assert result == {"A": "1", "B": "99", "C": "3"}


def test_update_vault_persists_changes(tmp_vault):
    create_vault(tmp_vault, PASSWORD, {"X": "old"})
    update_vault(tmp_vault, PASSWORD, {"X": "new"})
    assert read_vault(tmp_vault, PASSWORD)["X"] == "new"


def test_delete_key_removes_entry(tmp_vault):
    create_vault(tmp_vault, PASSWORD, {"KEEP": "yes", "REMOVE": "no"})
    result = delete_key(tmp_vault, PASSWORD, "REMOVE")
    assert "REMOVE" not in result
    assert result["KEEP"] == "yes"


def test_delete_key_missing_key_raises(tmp_vault):
    create_vault(tmp_vault, PASSWORD, {"A": "1"})
    with pytest.raises(KeyError):
        delete_key(tmp_vault, PASSWORD, "MISSING")
