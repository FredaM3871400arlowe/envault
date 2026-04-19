"""Integration tests for reminders CLI."""
import pytest
from click.testing import CliRunner
from envault.cli_reminders import reminders_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path):
    return str(tmp_path / "test.vault")


def test_set_then_list_shows_entry(runner, vault_path):
    runner.invoke(reminders_group, ["set", vault_path, "MY_KEY", "2099-12-31", "Year end review"])
    result = runner.invoke(reminders_group, ["list", vault_path])
    assert "MY_KEY" in result.output
    assert "Year end review" in result.output


def test_remove_then_show_returns_no_reminder(runner, vault_path):
    runner.invoke(reminders_group, ["set", vault_path, "DEL_KEY", "2099-01-01", "Delete me"])
    runner.invoke(reminders_group, ["remove", vault_path, "DEL_KEY"])
    result = runner.invoke(reminders_group, ["show", vault_path, "DEL_KEY"])
    assert "No reminder" in result.output


def test_multiple_keys_independent_reminders(runner, vault_path):
    runner.invoke(reminders_group, ["set", vault_path, "A", "2099-01-01", "msg A"])
    runner.invoke(reminders_group, ["set", vault_path, "B", "2099-06-01", "msg B"])
    r1 = runner.invoke(reminders_group, ["show", vault_path, "A"])
    r2 = runner.invoke(reminders_group, ["show", vault_path, "B"])
    assert "msg A" in r1.output
    assert "msg B" in r2.output
    assert "msg B" not in r1.output
