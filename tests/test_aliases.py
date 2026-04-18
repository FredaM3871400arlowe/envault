"""Unit tests for envault.aliases."""
from __future__ import annotations

import pytest

from envault.aliases import (
    _aliases_path,
    add_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    load_aliases,
)
from envault.vault import create_vault


@pytest.fixture()
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    create_vault(str(p), "password", {})
    return str(p)


def test_aliases_path_is_sibling_of_vault(vault_path, tmp_path):
    ap = _aliases_path(vault_path)
    assert ap.parent == tmp_path


def test_load_aliases_returns_empty_when_missing(vault_path):
    assert load_aliases(vault_path) == {}


def test_add_alias_creates_entry(vault_path):
    add_alias(vault_path, "db", "DATABASE_URL")
    assert load_aliases(vault_path)["db"] == "DATABASE_URL"


def test_add_alias_empty_alias_raises(vault_path):
    with pytest.raises(ValueError):
        add_alias(vault_path, "", "DATABASE_URL")


def test_add_alias_empty_key_raises(vault_path):
    with pytest.raises(ValueError):
        add_alias(vault_path, "db", "")


def test_remove_alias_deletes_entry(vault_path):
    add_alias(vault_path, "db", "DATABASE_URL")
    remove_alias(vault_path, "db")
    assert "db" not in load_aliases(vault_path)


def test_remove_unknown_alias_raises(vault_path):
    with pytest.raises(KeyError):
        remove_alias(vault_path, "nonexistent")


def test_resolve_alias_returns_key(vault_path):
    add_alias(vault_path, "db", "DATABASE_URL")
    assert resolve_alias(vault_path, "db") == "DATABASE_URL"


def test_resolve_alias_passthrough_when_not_found(vault_path):
    assert resolve_alias(vault_path, "UNKNOWN") == "UNKNOWN"


def test_list_aliases_returns_all(vault_path):
    add_alias(vault_path, "db", "DATABASE_URL")
    add_alias(vault_path, "secret", "SECRET_KEY")
    result = list_aliases(vault_path)
    assert result == {"db": "DATABASE_URL", "secret": "SECRET_KEY"}
