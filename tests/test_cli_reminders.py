"""Tests for envault.cli_reminders."""
import pytest
from click.testing import CliRunner
from envault.cli_reminders import reminders_group
from envault.reminders import set_reminder


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


def test_set_prints_confirmation(runner, vault_path):
    result = runner.invoke(reminders_group, ["set", vault_path, "DB_PASS", "2099-01-01", "Rotate!"])
    assert result.exit_code == 0
    assert "Reminder set" in result.output


def test_set_invalid_date_exits_nonzero(runner, vault_path):
    result = runner.invoke(reminders_group, ["set", vault_path, "KEY", "bad-date", "msg"])
    assert result.exit_code != 0


def test_show_existing_reminder(runner, vault_path):
    set_reminder(vault_path, "API", "Check this", "2099-05-01")
    result = runner.invoke(reminders_group, ["show", vault_path, "API"])
    assert result.exit_code == 0
    assert "Check this" in result.output


def test_show_missing_reminder(runner, vault_path):
    result = runner.invoke(reminders_group, ["show", vault_path, "GHOST"])
    assert "No reminder" in result.output


def test_remove_existing_reminder(runner, vault_path):
    set_reminder(vault_path, "TOKEN", "msg", "2099-01-01")
    result = runner.invoke(reminders_group, ["remove", vault_path, "TOKEN"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_unknown_reminder_exits_nonzero(runner, vault_path):
    result = runner.invoke(reminders_group, ["remove", vault_path, "NOPE"])
    assert result.exit_code != 0


def test_list_shows_all(runner, vault_path):
    set_reminder(vault_path, "K1", "first", "2099-01-01")
    set_reminder(vault_path, "K2", "second", "2099-02-01")
    result = runner.invoke(reminders_group, ["list", vault_path])
    assert "K1" in result.output
    assert "K2" in result.output


def test_due_shows_overdue(runner, vault_path):
    set_reminder(vault_path, "OLD", "stale", "2000-01-01")
    result = runner.invoke(reminders_group, ["due", vault_path])
    assert "OLD" in result.output
