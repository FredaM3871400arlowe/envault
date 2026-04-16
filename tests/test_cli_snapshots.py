"""Tests for envault.cli_snapshots."""
import pytest
from click.testing import CliRunner

from envault.cli_snapshots import snapshot_group
from envault.snapshots import take_snapshot
from envault.vault import create_vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_path(tmp_path):
    path = tmp_path / "test.vault"
    create_vault(str(path), "secret", initial_data={"FOO": "bar"})
    return str(path)


def test_take_prints_confirmation(runner, vault_path):
    result = runner.invoke(snapshot_group, ["take", vault_path, "--password", "secret", "--label", "v1"])
    assert result.exit_code == 0
    assert "Snapshot taken" in result.output
    assert "v1" in result.output


def test_take_wrong_password_exits_nonzero(runner, vault_path):
    result = runner.invoke(snapshot_group, ["take", vault_path, "--password", "wrong"])
    assert result.exit_code != 0


def test_list_shows_snapshots(runner, vault_path):
    take_snapshot(vault_path, "secret", label="snap1")
    result = runner.invoke(snapshot_group, ["list", vault_path])
    assert result.exit_code == 0
    assert "snap1" in result.output
    assert "[0]" in result.output


def test_list_empty_message(runner, vault_path):
    result = runner.invoke(snapshot_group, ["list", vault_path])
    assert "No snapshots found" in result.output


def test_delete_removes_snapshot(runner, vault_path):
    take_snapshot(vault_path, "secret", label="to_delete")
    result = runner.invoke(snapshot_group, ["delete", vault_path, "0"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_delete_invalid_index_shows_error(runner, vault_path):
    result = runner.invoke(snapshot_group, ["delete", vault_path, "99"])
    assert result.exit_code != 0
    assert "Error" in result.output
