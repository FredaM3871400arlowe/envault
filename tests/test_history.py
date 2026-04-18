"""Tests for envault.history."""
import pytest
from pathlib import Path
from envault.vault import create_vault
from envault.history import (
    _history_path,
    record_change,
    get_history,
    clear_history,
    load_history,
)


@pytest.fixture()
def vault_path(tmp_path):
    return create_vault(str(tmp_path / "test.vault"), "password", {})


def test_history_path_is_sibling_of_vault(vault_path):
    hp = _history_path(vault_path)
    assert hp.parent == Path(vault_path).parent
    assert hp.name.endswith(".history.json")


def test_load_history_returns_empty_when_missing(vault_path):
    assert load_history(vault_path) == {}


def test_record_change_creates_entry(vault_path):
    record_change(vault_path, "API_KEY", None, "abc123")
    records = get_history(vault_path, "API_KEY")
    assert len(records) == 1
    assert records[0]["old"] is None
    assert records[0]["new"] == "abc123"


def test_record_change_appends_multiple(vault_path):
    record_change(vault_path, "DB_URL", "old1", "old2")
    record_change(vault_path, "DB_URL", "old2", "new3")
    records = get_history(vault_path, "DB_URL")
    assert len(records) == 2
    assert records[-1]["new"] == "new3"


def test_record_change_includes_timestamp(vault_path):
    record_change(vault_path, "X", "a", "b")
    r = get_history(vault_path, "X")[0]
    assert "timestamp" in r
    assert "T" in r["timestamp"]  # ISO format


def test_get_history_missing_key_returns_empty(vault_path):
    assert get_history(vault_path, "NONEXISTENT") == []


def test_clear_history_single_key(vault_path):
    record_change(vault_path, "A", "1", "2")
    record_change(vault_path, "B", "x", "y")
    clear_history(vault_path, "A")
    assert get_history(vault_path, "A") == []
    assert len(get_history(vault_path, "B")) == 1


def test_clear_history_all_keys(vault_path):
    record_change(vault_path, "A", "1", "2")
    record_change(vault_path, "B", "x", "y")
    clear_history(vault_path)
    assert load_history(vault_path) == {}


def test_history_persists_across_calls(vault_path):
    record_change(vault_path, "KEY", "v1", "v2")
    record_change(vault_path, "KEY", "v2", "v3")
    fresh = get_history(vault_path, "KEY")
    assert fresh[0]["old"] == "v1"
    assert fresh[1]["new"] == "v3"
