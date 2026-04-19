"""Tests for envault.reminders."""
import pytest
from pathlib import Path
from envault.reminders import (
    _reminders_path, set_reminder, get_reminder, remove_reminder,
    list_due, load_reminders,
)


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "test.vault"


def test_reminders_path_is_sibling_of_vault(vault_path):
    p = _reminders_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == ".envault_reminders.json"


def test_load_reminders_returns_empty_when_missing(vault_path):
    assert load_reminders(vault_path) == {}


def test_set_reminder_creates_entry(vault_path):
    r = set_reminder(vault_path, "DB_PASS", "Rotate this!", "2099-01-01")
    assert r["message"] == "Rotate this!"
    assert r["due"] == "2099-01-01"


def test_set_reminder_persists(vault_path):
    set_reminder(vault_path, "API_KEY", "Check expiry", "2099-06-15")
    data = load_reminders(vault_path)
    assert "API_KEY" in data


def test_get_reminder_returns_entry(vault_path):
    set_reminder(vault_path, "SECRET", "Renew soon", "2099-03-10")
    r = get_reminder(vault_path, "SECRET")
    assert r is not None
    assert r["due"] == "2099-03-10"


def test_get_reminder_missing_key_returns_none(vault_path):
    assert get_reminder(vault_path, "MISSING") is None


def test_remove_reminder_deletes_entry(vault_path):
    set_reminder(vault_path, "TOKEN", "msg", "2099-01-01")
    assert remove_reminder(vault_path, "TOKEN") is True
    assert get_reminder(vault_path, "TOKEN") is None


def test_remove_reminder_missing_returns_false(vault_path):
    assert remove_reminder(vault_path, "GHOST") is False


def test_list_due_returns_overdue(vault_path):
    set_reminder(vault_path, "OLD_KEY", "very old", "2000-01-01")
    set_reminder(vault_path, "FUTURE_KEY", "not yet", "2099-01-01")
    due = list_due(vault_path)
    keys = [d["key"] for d in due]
    assert "OLD_KEY" in keys
    assert "FUTURE_KEY" not in keys


def test_list_due_with_as_of(vault_path):
    set_reminder(vault_path, "K1", "msg", "2030-06-01")
    due = list_due(vault_path, as_of="2030-06-01")
    assert any(d["key"] == "K1" for d in due)


def test_set_reminder_invalid_date_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid date format"):
        set_reminder(vault_path, "K", "msg", "not-a-date")
