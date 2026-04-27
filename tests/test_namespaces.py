"""Tests for envault.namespaces."""

from __future__ import annotations

import pytest

from envault.namespaces import (
    _namespaces_path,
    get_namespace,
    keys_in_namespace,
    list_namespaces,
    load_namespaces,
    remove_namespace,
    set_namespace,
)
from envault.vault import create_vault


@pytest.fixture()
def vault_path(tmp_path):
    return create_vault(tmp_path / "test.vault", "password")


def test_namespaces_path_is_sibling_of_vault(vault_path):
    p = _namespaces_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == ".envault_namespaces.json"


def test_load_namespaces_returns_empty_when_missing(vault_path):
    assert load_namespaces(vault_path) == {}


def test_set_and_get_namespace(vault_path):
    set_namespace(vault_path, "DB_HOST", "database")
    assert get_namespace(vault_path, "DB_HOST") == "database"


def test_get_namespace_missing_key_returns_none(vault_path):
    assert get_namespace(vault_path, "MISSING") is None


def test_set_namespace_empty_namespace_raises(vault_path):
    with pytest.raises(ValueError, match="Namespace must not be empty"):
        set_namespace(vault_path, "KEY", "   ")


def test_set_namespace_empty_key_raises(vault_path):
    with pytest.raises(ValueError, match="Key must not be empty"):
        set_namespace(vault_path, "  ", "myns")


def test_remove_namespace(vault_path):
    set_namespace(vault_path, "API_KEY", "secrets")
    remove_namespace(vault_path, "API_KEY")
    assert get_namespace(vault_path, "API_KEY") is None


def test_remove_namespace_nonexistent_is_noop(vault_path):
    remove_namespace(vault_path, "NONEXISTENT")
    assert load_namespaces(vault_path) == {}


def test_keys_in_namespace(vault_path):
    set_namespace(vault_path, "DB_HOST", "database")
    set_namespace(vault_path, "DB_PORT", "database")
    set_namespace(vault_path, "API_KEY", "secrets")
    keys = keys_in_namespace(vault_path, "database")
    assert keys == ["DB_HOST", "DB_PORT"]


def test_keys_in_namespace_empty_when_none_match(vault_path):
    set_namespace(vault_path, "API_KEY", "secrets")
    assert keys_in_namespace(vault_path, "database") == []


def test_list_namespaces_returns_distinct(vault_path):
    set_namespace(vault_path, "DB_HOST", "database")
    set_namespace(vault_path, "DB_PORT", "database")
    set_namespace(vault_path, "API_KEY", "secrets")
    ns_list = list_namespaces(vault_path)
    assert ns_list == ["database", "secrets"]


def test_list_namespaces_empty_when_none_defined(vault_path):
    assert list_namespaces(vault_path) == []


def test_overwrite_namespace(vault_path):
    set_namespace(vault_path, "DB_HOST", "old")
    set_namespace(vault_path, "DB_HOST", "new")
    assert get_namespace(vault_path, "DB_HOST") == "new"
    assert list_namespaces(vault_path) == ["new"]
