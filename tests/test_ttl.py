"""Tests for envault/ttl.py"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envault.vault import create_vault
from envault.ttl import (
    _ttl_path,
    set_ttl,
    get_ttl,
    clear_ttl,
    list_expired,
    purge_expired,
)

PASSWORD = "hunter2"


@pytest.fixture
def vault_path(tmp_path):
    return create_vault(tmp_path / "test.vault", PASSWORD)


def test_ttl_path_is_sibling_of_vault(vault_path):
    p = _ttl_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name.endswith(".ttl.json")


def test_set_ttl_returns_datetime(vault_path):
    from datetime import datetime
    dt = set_ttl(vault_path, "API_KEY", 3600)
    assert isinstance(dt, datetime)


def test_get_ttl_returns_none_when_missing(vault_path):
    assert get_ttl(vault_path, "MISSING") is None


def test_set_and_get_ttl_roundtrip(vault_path):
    set_ttl(vault_path, "DB_PASS", 3600)
    dt = get_ttl(vault_path, "DB_PASS")
    assert dt is not None


def test_set_ttl_invalid_seconds_raises(vault_path):
    with pytest.raises(ValueError):
        set_ttl(vault_path, "KEY", 0)
    with pytest.raises(ValueError):
        set_ttl(vault_path, "KEY", -10)


def test_clear_ttl_removes_entry(vault_path):
    set_ttl(vault_path, "TOKEN", 3600)
    removed = clear_ttl(vault_path, "TOKEN")
    assert removed is True
    assert get_ttl(vault_path, "TOKEN") is None


def test_clear_ttl_missing_returns_false(vault_path):
    assert clear_ttl(vault_path, "NOPE") is False


def test_list_expired_finds_elapsed_key(vault_path):
    set_ttl(vault_path, "OLD_KEY", 1)
    time.sleep(1.1)
    expired = list_expired(vault_path)
    assert "OLD_KEY" in expired


def test_list_expired_excludes_future_key(vault_path):
    set_ttl(vault_path, "FUTURE_KEY", 3600)
    expired = list_expired(vault_path)
    assert "FUTURE_KEY" not in expired


def test_purge_expired_removes_elapsed(vault_path):
    set_ttl(vault_path, "STALE", 1)
    time.sleep(1.1)
    purged = purge_expired(vault_path)
    assert "STALE" in purged
    assert get_ttl(vault_path, "STALE") is None


def test_purge_expired_returns_empty_when_none(vault_path):
    set_ttl(vault_path, "LIVE", 3600)
    purged = purge_expired(vault_path)
    assert purged == []
