"""Integration tests: pins survive repeated add calls and interact correctly."""
import pytest
from click.testing import CliRunner
from envault.vault import create_vault
from envault.cli_pins import pins_group
from envault.pins import is_pinned, list_pins


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path):
    return create_vault(str(tmp_path / "vault"), "pass")


def test_pin_persists_after_second_add(runner, vault_path):
    runner.invoke(pins_group, ["add", str(vault_path), "DB_URL"])
    runner.invoke(pins_group, ["add", str(vault_path), "DB_URL"])
    assert list_pins(vault_path).count("DB_URL") == 1


def test_multiple_keys_independently_pinned(runner, vault_path):
    for k in ["A", "B", "C"]:
        runner.invoke(pins_group, ["add", str(vault_path), k])
    runner.invoke(pins_group, ["remove", str(vault_path), "B"])
    assert is_pinned(vault_path, "A") is True
    assert is_pinned(vault_path, "B") is False
    assert is_pinned(vault_path, "C") is True


def test_remove_then_re_add(runner, vault_path):
    runner.invoke(pins_group, ["add", str(vault_path), "KEY"])
    runner.invoke(pins_group, ["remove", str(vault_path), "KEY"])
    runner.invoke(pins_group, ["add", str(vault_path), "KEY"])
    assert is_pinned(vault_path, "KEY") is True
