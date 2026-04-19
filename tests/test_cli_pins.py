import pytest
from click.testing import CliRunner
from envault.vault import create_vault
from envault.cli_pins import pins_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path):
    return create_vault(str(tmp_path / "vault"), "pass")


def test_add_prints_confirmation(runner, vault_path):
    result = runner.invoke(pins_group, ["add", str(vault_path), "DB_URL"])
    assert result.exit_code == 0
    assert "Pinned" in result.output


def test_remove_prints_confirmation(runner, vault_path):
    runner.invoke(pins_group, ["add", str(vault_path), "DB_URL"])
    result = runner.invoke(pins_group, ["remove", str(vault_path), "DB_URL"])
    assert result.exit_code == 0
    assert "Unpinned" in result.output


def test_remove_unknown_shows_error(runner, vault_path):
    result = runner.invoke(pins_group, ["remove", str(vault_path), "GHOST"])
    assert result.exit_code != 0


def test_list_shows_pinned_keys(runner, vault_path):
    runner.invoke(pins_group, ["add", str(vault_path), "KEY_A"])
    runner.invoke(pins_group, ["add", str(vault_path), "KEY_B"])
    result = runner.invoke(pins_group, ["list", str(vault_path)])
    assert "KEY_A" in result.output
    assert "KEY_B" in result.output


def test_list_empty_shows_message(runner, vault_path):
    result = runner.invoke(pins_group, ["list", str(vault_path)])
    assert "No pinned keys" in result.output


def test_check_pinned(runner, vault_path):
    runner.invoke(pins_group, ["add", str(vault_path), "X"])
    result = runner.invoke(pins_group, ["check", str(vault_path), "X"])
    assert "is pinned" in result.output


def test_check_not_pinned(runner, vault_path):
    result = runner.invoke(pins_group, ["check", str(vault_path), "Y"])
    assert "not pinned" in result.output
