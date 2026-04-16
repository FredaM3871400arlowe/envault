"""Tests for envault.cli_tags."""
import pytest
from click.testing import CliRunner
from envault.vault import create_vault
from envault.cli_tags import tags_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path):
    return create_vault(tmp_path / "test.vault", "pass")


def test_add_prints_confirmation(runner, vault_path):
    result = runner.invoke(tags_group, ["add", str(vault_path), "MY_KEY", "prod"])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_remove_prints_confirmation(runner, vault_path):
    runner.invoke(tags_group, ["add", str(vault_path), "MY_KEY", "prod"])
    result = runner.invoke(tags_group, ["remove", str(vault_path), "MY_KEY", "prod"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_unknown_tag_shows_error(runner, vault_path):
    result = runner.invoke(tags_group, ["remove", str(vault_path), "MY_KEY", "ghost"])
    assert result.exit_code != 0


def test_list_shows_tags(runner, vault_path):
    runner.invoke(tags_group, ["add", str(vault_path), "K", "alpha"])
    runner.invoke(tags_group, ["add", str(vault_path), "K", "beta"])
    result = runner.invoke(tags_group, ["list", str(vault_path), "K"])
    assert "alpha" in result.output
    assert "beta" in result.output


def test_list_no_tags_message(runner, vault_path):
    result = runner.invoke(tags_group, ["list", str(vault_path), "MISSING"])
    assert "No tags" in result.output


def test_find_keys_with_tag(runner, vault_path):
    runner.invoke(tags_group, ["add", str(vault_path), "A", "prod"])
    runner.invoke(tags_group, ["add", str(vault_path), "B", "prod"])
    result = runner.invoke(tags_group, ["find", str(vault_path), "prod"])
    assert "A" in result.output
    assert "B" in result.output
