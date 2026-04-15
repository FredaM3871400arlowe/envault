"""Tests for envault.audit module."""

import json
from pathlib import Path

import pytest

from envault.audit import (
    AUDIT_LOG_FILENAME,
    clear_events,
    read_events,
    record_event,
    _audit_log_path,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> str:
    p = tmp_path / "test.vault"
    p.touch()
    return str(p)


def test_audit_log_path_is_sibling_of_vault(vault_path: str) -> None:
    log = _audit_log_path(vault_path)
    assert log.name == AUDIT_LOG_FILENAME
    assert log.parent == Path(vault_path).parent


def test_record_event_creates_log_file(vault_path: str) -> None:
    record_event(vault_path, action="init")
    log = _audit_log_path(vault_path)
    assert log.exists()


def test_record_event_writes_valid_json(vault_path: str) -> None:
    record_event(vault_path, action="set", key="DB_URL")
    log = _audit_log_path(vault_path)
    line = log.read_text(encoding="utf-8").strip()
    data = json.loads(line)
    assert data["action"] == "set"
    assert data["key"] == "DB_URL"


def test_record_event_includes_timestamp(vault_path: str) -> None:
    record_event(vault_path, action="get", key="SECRET")
    events = read_events(vault_path)
    assert "timestamp" in events[0]
    assert events[0]["timestamp"].endswith("+00:00")


def test_record_event_custom_actor(vault_path: str) -> None:
    record_event(vault_path, action="delete", key="OLD_KEY", actor="alice")
    events = read_events(vault_path)
    assert events[0]["actor"] == "alice"


def test_multiple_events_appended(vault_path: str) -> None:
    record_event(vault_path, action="set", key="A")
    record_event(vault_path, action="set", key="B")
    record_event(vault_path, action="get", key="A")
    events = read_events(vault_path)
    assert len(events) == 3
    assert events[0]["key"] == "A"
    assert events[2]["action"] == "get"


def test_read_events_returns_empty_list_when_no_log(vault_path: str) -> None:
    events = read_events(vault_path)
    assert events == []


def test_clear_events_removes_log(vault_path: str) -> None:
    record_event(vault_path, action="init")
    clear_events(vault_path)
    assert not _audit_log_path(vault_path).exists()


def test_clear_events_noop_when_no_log(vault_path: str) -> None:
    # Should not raise even if log does not exist
    clear_events(vault_path)
