"""Tests for envault.locks."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.locks import (
    _locks_path,
    load_locks,
    lock_key,
    unlock_key,
    is_locked,
    assert_not_locked,
)
from envault.vault import create_vault


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(tmp_path / "test.vault", "secret")


def test_locks_path_is_sibling_of_vault(vault_path: Path) -> None:
    lp = _locks_path(vault_path)
    assert lp.parent == vault_path.parent
    assert lp.name == "test.locks.json"


def test_load_locks_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_locks(vault_path) == []


def test_lock_key_creates_entry(vault_path: Path) -> None:
    result = lock_key(vault_path, "API_KEY")
    assert "API_KEY" in result


def test_lock_key_persists(vault_path: Path) -> None:
    lock_key(vault_path, "DB_PASSWORD")
    assert is_locked(vault_path, "DB_PASSWORD")


def test_lock_key_no_duplicates(vault_path: Path) -> None:
    lock_key(vault_path, "SECRET")
    lock_key(vault_path, "SECRET")
    locks = load_locks(vault_path)
    assert locks.count("SECRET") == 1


def test_lock_key_empty_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="empty"):
        lock_key(vault_path, "")


def test_unlock_key_removes_entry(vault_path: Path) -> None:
    lock_key(vault_path, "TOKEN")
    result = unlock_key(vault_path, "TOKEN")
    assert "TOKEN" not in result
    assert not is_locked(vault_path, "TOKEN")


def test_unlock_unknown_key_raises(vault_path: Path) -> None:
    with pytest.raises(KeyError, match="not locked"):
        unlock_key(vault_path, "NONEXISTENT")


def test_is_locked_false_when_not_locked(vault_path: Path) -> None:
    assert not is_locked(vault_path, "SOME_KEY")


def test_assert_not_locked_passes_for_unlocked_key(vault_path: Path) -> None:
    assert_not_locked(vault_path, "SAFE_KEY")  # should not raise


def test_assert_not_locked_raises_for_locked_key(vault_path: Path) -> None:
    lock_key(vault_path, "CRITICAL")
    with pytest.raises(RuntimeError, match="locked"):
        assert_not_locked(vault_path, "CRITICAL")


def test_multiple_keys_independently_locked(vault_path: Path) -> None:
    lock_key(vault_path, "KEY_A")
    lock_key(vault_path, "KEY_B")
    assert is_locked(vault_path, "KEY_A")
    assert is_locked(vault_path, "KEY_B")
    unlock_key(vault_path, "KEY_A")
    assert not is_locked(vault_path, "KEY_A")
    assert is_locked(vault_path, "KEY_B")
