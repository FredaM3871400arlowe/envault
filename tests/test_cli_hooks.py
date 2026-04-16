import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_hooks import hooks_group
from envault.vault import create_vault


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path):
    p = create_vault(tmp_path / "test.vault", "secret", {})
    return str(p)


def test_add_prints_confirmation(runner, vault_path):
    result = runner.invoke(hooks_group, ["add", vault_path, "--event", "post-set", "--cmd", "echo done"])
    assert result.exit_code == 0
    assert "Hook added" in result.output


def test_remove_prints_confirmation(runner, vault_path):
    runner.invoke(hooks_group, ["add", vault_path, "--event", "post-set", "--cmd", "echo done"])
    result = runner.invoke(hooks_group, ["remove", vault_path, "--event", "post-set", "--cmd", "echo done"])
    assert result.exit_code == 0
    assert "Hook removed" in result.output


def test_remove_unknown_hook_shows_error(runner, vault_path):
    result = runner.invoke(hooks_group, ["remove", vault_path, "--event", "post-set", "--cmd", "echo missing"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_list_shows_hooks(runner, vault_path):
    runner.invoke(hooks_group, ["add", vault_path, "--event", "post-get", "--cmd", "echo hello"])
    result = runner.invoke(hooks_group, ["list", vault_path])
    assert result.exit_code == 0
    assert "post-get" in result.output
    assert "echo hello" in result.output


def test_list_empty_shows_message(runner, vault_path):
    result = runner.invoke(hooks_group, ["list", vault_path])
    assert result.exit_code == 0
    assert "No hooks" in result.output


def test_add_invalid_event_shows_error(runner, vault_path):
    result = runner.invoke(hooks_group, ["add", vault_path, "--event", "invalid-event", "--cmd", "echo x"])
    assert result.exit_code != 0
    assert "Error" in result.output
