import pytest
from pathlib import Path
from envault.notes import (
    _notes_path, set_note, get_note, remove_note, list_notes,
    load_notes, save_notes,
)


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "test.vault"


def test_notes_path_is_sibling_of_vault(vault_path):
    p = _notes_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.notes.json"


def test_load_notes_returns_empty_when_missing(vault_path):
    assert load_notes(vault_path) == {}


def test_set_and_get_note(vault_path):
    set_note(vault_path, "DB_URL", "Postgres connection string")
    assert get_note(vault_path, "DB_URL") == "Postgres connection string"


def test_get_note_missing_key_returns_none(vault_path):
    assert get_note(vault_path, "MISSING") is None


def test_set_note_overwrites_existing(vault_path):
    set_note(vault_path, "KEY", "first")
    set_note(vault_path, "KEY", "second")
    assert get_note(vault_path, "KEY") == "second"


def test_remove_note_deletes_entry(vault_path):
    set_note(vault_path, "API_KEY", "some note")
    remove_note(vault_path, "API_KEY")
    assert get_note(vault_path, "API_KEY") is None


def test_remove_note_missing_key_raises(vault_path):
    with pytest.raises(KeyError):
        remove_note(vault_path, "GHOST")


def test_list_notes_returns_all(vault_path):
    set_note(vault_path, "A", "note a")
    set_note(vault_path, "B", "note b")
    notes = list_notes(vault_path)
    assert notes == {"A": "note a", "B": "note b"}


def test_save_and_load_roundtrip(vault_path):
    data = {"X": "hello", "Y": "world"}
    save_notes(vault_path, data)
    assert load_notes(vault_path) == data
