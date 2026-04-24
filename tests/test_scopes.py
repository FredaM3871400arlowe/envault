"""Unit tests for envault/scopes.py."""
from __future__ import annotations

import pytest

from envault.scopes import (
    _scopes_path,
    get_scope,
    keys_in_scope,
    load_scopes,
    remove_scope,
    set_scope,
)


@pytest.fixture()
def vault_path(tmp_path):
    return tmp_path / "test.vault"


def test_scopes_path_is_sibling_of_vault(vault_path):
    p = _scopes_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.scopes.json"


def test_load_scopes_returns_empty_when_missing(vault_path):
    assert load_scopes(vault_path) == {}


def test_set_and_get_scope(vault_path):
    set_scope(vault_path, "DATABASE_URL", "prod")
    assert get_scope(vault_path, "DATABASE_URL") == "prod"


def test_get_scope_missing_key_returns_none(vault_path):
    assert get_scope(vault_path, "MISSING_KEY") is None


def test_set_scope_invalid_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid scope"):
        set_scope(vault_path, "KEY", "production")


def test_set_scope_persists(vault_path):
    set_scope(vault_path, "API_KEY", "staging")
    # reload from disk
    assert load_scopes(vault_path)["API_KEY"] == "staging"


def test_remove_scope_deletes_entry(vault_path):
    set_scope(vault_path, "SECRET", "dev")
    remove_scope(vault_path, "SECRET")
    assert get_scope(vault_path, "SECRET") is None


def test_remove_scope_noop_when_absent(vault_path):
    remove_scope(vault_path, "NONEXISTENT")  # should not raise


def test_keys_in_scope_filters_correctly(vault_path):
    set_scope(vault_path, "A", "dev")
    set_scope(vault_path, "B", "prod")
    set_scope(vault_path, "C", "dev")
    assert sorted(keys_in_scope(vault_path, "dev")) == ["A", "C"]
    assert keys_in_scope(vault_path, "prod") == ["B"]


def test_keys_in_scope_empty_when_none_match(vault_path):
    set_scope(vault_path, "X", "ci")
    assert keys_in_scope(vault_path, "test") == []


def test_overwrite_scope(vault_path):
    set_scope(vault_path, "TOKEN", "dev")
    set_scope(vault_path, "TOKEN", "prod")
    assert get_scope(vault_path, "TOKEN") == "prod"
