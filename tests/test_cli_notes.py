import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_notes import notes_group
from envault.notes import set_note


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


def test_set_prints_confirmation(runner, vault_path):
    result = runner.invoke(notes_group, ["set", vault_path, "DB_URL", "main db"])
    assert result.exit_code == 0
    assert "Note set for 'DB_URL'" in result.output


def test_get_existing_note(runner, vault_path):
    set_note(vault_path, "SECRET", "do not share")
    result = runner.invoke(notes_group, ["get", vault_path, "SECRET"])
    assert result.exit_code == 0
    assert "do not share" in result.output


def test_get_missing_note(runner, vault_path):
    result = runner.invoke(notes_group, ["get", vault_path, "NOPE"])
    assert result.exit_code == 0
    assert "No note" in result.output


def test_remove_prints_confirmation(runner, vault_path):
    set_note(vault_path, "KEY", "a note")
    result = runner.invoke(notes_group, ["remove", vault_path, "KEY"])
    assert result.exit_code == 0
    assert "Note removed for 'KEY'" in result.output


def test_remove_unknown_shows_error(runner, vault_path):
    result = runner.invoke(notes_group, ["remove", vault_path, "GHOST"])
    assert result.exit_code != 0


def test_list_shows_all_notes(runner, vault_path):
    set_note(vault_path, "A", "alpha")
    set_note(vault_path, "B", "beta")
    result = runner.invoke(notes_group, ["list", vault_path])
    assert "A: alpha" in result.output
    assert "B: beta" in result.output


def test_list_empty_vault(runner, vault_path):
    result = runner.invoke(notes_group, ["list", vault_path])
    assert "No notes found" in result.output
