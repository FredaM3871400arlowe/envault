"""Tests for envault/status.py"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envault.vault import create_vault, update_vault
from envault.locks import lock_key
from envault.pins import pin_key
from envault.expiry import set_expiry
from envault.ttl import set_ttl
from envault.status import get_key_status, get_all_statuses, format_status


PASSWORD = "statuspass"


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    p = create_vault(tmp_path / "status_test", PASSWORD)
    update_vault(p, PASSWORD, {"API_KEY": "abc123", "DB_URL": "postgres://localhost"})
    return p


def test_default_status_is_healthy(vault_path):
    status = get_key_status(vault_path, "API_KEY")
    assert status.healthy
    assert status.summary() == "ok"


def test_locked_key_shows_locked(vault_path):
    lock_key(vault_path, "API_KEY", reason="test")
    status = get_key_status(vault_path, "API_KEY")
    assert status.locked is True
    assert "locked" in status.summary()


def test_pinned_key_shows_pinned(vault_path):
    pin_key(vault_path, "API_KEY")
    status = get_key_status(vault_path, "API_KEY")
    assert status.pinned is True
    assert "pinned" in status.summary()


def test_expired_key_shows_expired(vault_path):
    past = datetime.now(tz=timezone.utc) - timedelta(days=1)
    set_expiry(vault_path, "API_KEY", past)
    status = get_key_status(vault_path, "API_KEY")
    assert status.expired is True
    assert status.healthy is False
    assert "expired" in status.summary()


def test_future_expiry_not_expired(vault_path):
    future = datetime.now(tz=timezone.utc) + timedelta(days=30)
    set_expiry(vault_path, "API_KEY", future)
    status = get_key_status(vault_path, "API_KEY")
    assert status.expired is False
    assert status.healthy is True


def test_elapsed_ttl_shows_ttl_elapsed(vault_path):
    set_ttl(vault_path, "DB_URL", seconds=0)
    status = get_key_status(vault_path, "DB_URL")
    assert status.ttl_elapsed is True
    assert status.healthy is False


def test_get_all_statuses_returns_one_per_key(vault_path):
    statuses = get_all_statuses(vault_path, ["API_KEY", "DB_URL"])
    assert len(statuses) == 2
    keys = {s.key for s in statuses}
    assert keys == {"API_KEY", "DB_URL"}


def test_format_status_ok(vault_path):
    status = get_key_status(vault_path, "API_KEY")
    line = format_status(status)
    assert "API_KEY" in line
    assert "ok" in line


def test_format_status_multiple_flags(vault_path):
    lock_key(vault_path, "API_KEY", reason="test")
    pin_key(vault_path, "API_KEY")
    status = get_key_status(vault_path, "API_KEY")
    line = format_status(status)
    assert "[LOCKED]" in line
    assert "[PINNED]" in line
