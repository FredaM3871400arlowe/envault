"""Integration tests: notes survive set/overwrite cycles."""
import pytest
from click.testing import CliRunner
from envault.cli_notes import notes_group
from envault.notes import set_note, get_note


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / "env.vault")


def test_note_persists_after_second_set(runner, vault_path):
    runner.invoke(notes_group, ["set", vault_path, "KEY", "first note"])
    runner.invoke(notes_group, ["set", vault_path, "KEY", "updated note"])
    assert get_note(vault_path, "KEY") == "updated note"


def test_multiple_keys_independent_notes(vault_path):
    set_note(vault_path, "A", "note a")
    set_note(vault_path, "B", "note b")
    assert get_note(vault_path, "A") == "note a"
    assert get_note(vault_path, "B") == "note b"


def test_remove_does_not_affect_other_keys(vault_path):
    set_note(vault_path, "A", "keep")
    set_note(vault_path, "B", "remove me")
    from envault.notes import remove_note
    remove_note(vault_path, "B")
    assert get_note(vault_path, "A") == "keep"
    assert get_note(vault_path, "B") is None
