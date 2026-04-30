"""Integration tests for approval workflow CLI."""
import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.vault import create_vault
from envault.cli_approvals import approvals_group
from envault.approvals import load_approvals


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path):
    return create_vault(tmp_path / "test.vault", "password")


def test_request_then_approve_then_list_shows_approved(runner, vault_path):
    runner.invoke(approvals_group, ["request", str(vault_path), "DB_PASS", "--requestor", "alice"])
    runner.invoke(approvals_group, ["approve", str(vault_path), "DB_PASS", "--reviewer", "bob"])
    result = runner.invoke(approvals_group, ["list", str(vault_path)])
    assert "approved" in result.output


def test_remove_then_show_returns_no_record(runner, vault_path):
    runner.invoke(approvals_group, ["request", str(vault_path), "KEY", "--requestor", "alice"])
    runner.invoke(approvals_group, ["remove", str(vault_path), "KEY"])
    result = runner.invoke(approvals_group, ["show", str(vault_path), "KEY"])
    assert "No approval record" in result.output


def test_multiple_keys_independent_approvals(runner, vault_path):
    for key in ["KEY_X", "KEY_Y", "KEY_Z"]:
        runner.invoke(approvals_group, ["request", str(vault_path), key, "--requestor", "alice"])
    runner.invoke(approvals_group, ["approve", str(vault_path), "KEY_Y", "--reviewer", "bob"])
    data = load_approvals(vault_path)
    assert data["KEY_X"]["state"] == "pending"
    assert data["KEY_Y"]["state"] == "approved"
    assert data["KEY_Z"]["state"] == "pending"


def test_double_approve_exits_nonzero(runner, vault_path):
    runner.invoke(approvals_group, ["request", str(vault_path), "ONCE", "--requestor", "alice"])
    runner.invoke(approvals_group, ["approve", str(vault_path), "ONCE", "--reviewer", "bob"])
    result = runner.invoke(approvals_group, ["approve", str(vault_path), "ONCE", "--reviewer", "carol"])
    assert result.exit_code != 0
