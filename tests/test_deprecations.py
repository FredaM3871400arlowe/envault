"""Tests for envault.deprecations."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.deprecations import (
    _deprecations_path,
    deprecate_key,
    get_deprecation,
    list_deprecated,
    load_deprecations,
    undeprecate_key,
)
from envault.vault import create_vault


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    return create_vault(tmp_path / "test.vault", "password")


def test_deprecations_path_is_sibling_of_vault(vault_path: Path) -> None:
    p = _deprecations_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.deprecations.json"


def test_load_deprecations_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_deprecations(vault_path) == {}


def test_deprecate_key_creates_entry(vault_path: Path) -> None:
    entry = deprecate_key(vault_path, "OLD_API_KEY", reason="Replaced by NEW_API_KEY")
    assert entry["reason"] == "Replaced by NEW_API_KEY"
    assert "deprecated_on" in entry


def test_deprecate_key_persists(vault_path: Path) -> None:
    deprecate_key(vault_path, "OLD_API_KEY", reason="No longer needed")
    data = load_deprecations(vault_path)
    assert "OLD_API_KEY" in data


def test_deprecate_key_with_removal_date(vault_path: Path) -> None:
    entry = deprecate_key(
        vault_path, "LEGACY_TOKEN", reason="Expiring soon", removal_date="2025-12-31"
    )
    assert entry["removal_date"] == "2025-12-31"


def test_deprecate_key_with_replacement(vault_path: Path) -> None:
    entry = deprecate_key(
        vault_path, "DB_PASS", reason="Renamed", replacement="DATABASE_PASSWORD"
    )
    assert entry["replacement"] == "DATABASE_PASSWORD"


def test_deprecate_key_invalid_date_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError):
        deprecate_key(vault_path, "KEY", reason="test", removal_date="not-a-date")


def test_deprecate_key_empty_key_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError):
        deprecate_key(vault_path, "", reason="test")


def test_deprecate_key_empty_reason_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError):
        deprecate_key(vault_path, "SOME_KEY", reason="")


def test_get_deprecation_returns_entry(vault_path: Path) -> None:
    deprecate_key(vault_path, "SOME_KEY", reason="Old")
    entry = get_deprecation(vault_path, "SOME_KEY")
    assert entry is not None
    assert entry["reason"] == "Old"


def test_get_deprecation_missing_key_returns_none(vault_path: Path) -> None:
    assert get_deprecation(vault_path, "MISSING") is None


def test_undeprecate_key_removes_entry(vault_path: Path) -> None:
    deprecate_key(vault_path, "OLD", reason="done")
    undeprecate_key(vault_path, "OLD")
    assert get_deprecation(vault_path, "OLD") is None


def test_undeprecate_unknown_key_raises(vault_path: Path) -> None:
    with pytest.raises(KeyError):
        undeprecate_key(vault_path, "DOES_NOT_EXIST")


def test_list_deprecated_returns_all(vault_path: Path) -> None:
    deprecate_key(vault_path, "A", reason="old")
    deprecate_key(vault_path, "B", reason="renamed")
    result = list_deprecated(vault_path)
    assert set(result.keys()) == {"A", "B"}
