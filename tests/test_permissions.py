"""Tests for envault/permissions.py."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.permissions import (
    _permissions_path,
    load_permissions,
    save_permissions,
    set_permissions,
    get_permissions,
    add_permission,
    remove_permission,
    has_permission,
    clear_permissions,
    VALID_PERMISSIONS,
)


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "test.vault"


def test_permissions_path_is_sibling_of_vault(vault_path: Path) -> None:
    p = _permissions_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.permissions.json"


def test_load_permissions_returns_empty_when_missing(vault_path: Path) -> None:
    result = load_permissions(vault_path)
    assert result == {}


def test_set_and_get_permissions(vault_path: Path) -> None:
    set_permissions(vault_path, "API_KEY", ["read"])
    assert get_permissions(vault_path, "API_KEY") == ["read"]


def test_get_permissions_defaults_to_all(vault_path: Path) -> None:
    perms = get_permissions(vault_path, "MISSING_KEY")
    assert set(perms) == VALID_PERMISSIONS


def test_set_permissions_invalid_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid permissions"):
        set_permissions(vault_path, "KEY", ["read", "execute"])


def test_set_permissions_replaces_existing(vault_path: Path) -> None:
    set_permissions(vault_path, "DB_URL", ["read", "write"])
    set_permissions(vault_path, "DB_URL", ["read"])
    assert get_permissions(vault_path, "DB_URL") == ["read"]


def test_add_permission_creates_entry(vault_path: Path) -> None:
    add_permission(vault_path, "SECRET", "read")
    assert "read" in get_permissions(vault_path, "SECRET")


def test_add_permission_no_duplicates(vault_path: Path) -> None:
    set_permissions(vault_path, "KEY", ["read"])
    add_permission(vault_path, "KEY", "read")
    assert get_permissions(vault_path, "KEY").count("read") == 1


def test_add_permission_invalid_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid permission"):
        add_permission(vault_path, "KEY", "execute")


def test_remove_permission(vault_path: Path) -> None:
    set_permissions(vault_path, "KEY", ["read", "write"])
    remove_permission(vault_path, "KEY", "write")
    assert get_permissions(vault_path, "KEY") == ["read"]


def test_remove_permission_invalid_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid permission"):
        remove_permission(vault_path, "KEY", "fly")


def test_has_permission_true(vault_path: Path) -> None:
    set_permissions(vault_path, "KEY", ["read", "delete"])
    assert has_permission(vault_path, "KEY", "read") is True


def test_has_permission_false(vault_path: Path) -> None:
    set_permissions(vault_path, "KEY", ["read"])
    assert has_permission(vault_path, "KEY", "write") is False


def test_clear_permissions_removes_entry(vault_path: Path) -> None:
    set_permissions(vault_path, "KEY", ["read"])
    clear_permissions(vault_path, "KEY")
    assert set(get_permissions(vault_path, "KEY")) == VALID_PERMISSIONS


def test_save_and_load_roundtrip(vault_path: Path) -> None:
    data = {"A": ["read"], "B": ["delete", "write"]}
    save_permissions(vault_path, data)
    assert load_permissions(vault_path) == data
