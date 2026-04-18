"""Tests for envault.expiry."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envault.vault import create_vault
from envault.expiry import (
    _expiry_path,
    set_expiry,
    clear_expiry,
    get_expiry,
    expired_keys,
    purge_expired,
)

PASSWORD = "test-pass"


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    path = create_vault(tmp_path / "test.vault", PASSWORD, {"KEY1": "val1", "KEY2": "val2"})
    return path


def test_expiry_path_is_sibling_of_vault(vault_path: Path) -> None:
    ep = _expiry_path(vault_path)
    assert ep.parent == vault_path.parent
    assert ep.name == "test.expiry.json"


def test_set_and_get_expiry(vault_path: Path) -> None:
    future = datetime.now(timezone.utc) + timedelta(days=10)
    set_expiry(vault_path, "KEY1", future)
    result = get_expiry(vault_path, "KEY1")
    assert result is not None
    assert abs((result - future).total_seconds()) < 1


def test_get_expiry_missing_key_returns_none(vault_path: Path) -> None:
    assert get_expiry(vault_path, "MISSING") is None


def test_clear_expiry_removes_key(vault_path: Path) -> None:
    future = datetime.now(timezone.utc) + timedelta(days=5)
    set_expiry(vault_path, "KEY1", future)
    clear_expiry(vault_path, "KEY1")
    assert get_expiry(vault_path, "KEY1") is None


def test_clear_expiry_nonexistent_key_is_noop(vault_path: Path) -> None:
    clear_expiry(vault_path, "NOPE")  # should not raise


def test_expired_keys_returns_past_keys(vault_path: Path) -> None:
    past = datetime.now(timezone.utc) - timedelta(seconds=1)
    future = datetime.now(timezone.utc) + timedelta(days=1)
    set_expiry(vault_path, "KEY1", past)
    set_expiry(vault_path, "KEY2", future)
    result = expired_keys(vault_path)
    assert "KEY1" in result
    assert "KEY2" not in result


def test_expired_keys_empty_when_none_expired(vault_path: Path) -> None:
    future = datetime.now(timezone.utc) + timedelta(days=1)
    set_expiry(vault_path, "KEY1", future)
    assert expired_keys(vault_path) == []


def test_purge_expired_removes_from_vault(vault_path: Path) -> None:
    past = datetime.now(timezone.utc) - timedelta(seconds=1)
    set_expiry(vault_path, "KEY1", past)
    removed = purge_expired(vault_path, PASSWORD)
    assert "KEY1" in removed
    from envault.vault import read_vault
    env = read_vault(vault_path, PASSWORD)
    assert "KEY1" not in env
    assert get_expiry(vault_path, "KEY1") is None


def test_purge_expired_no_expired_returns_empty(vault_path: Path) -> None:
    assert purge_expired(vault_path, PASSWORD) == []
