"""Tests for the approvals CLI commands."""
import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.vault import create_vault
from envault.cli_approvals import approvals_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path):
    return create_vault(tmp_path / "test.vault", "password")


def test_request_prints_confirmation(runner, vault_path):
    result = runner.invoke(
        approvals_group,
        ["request", str(vault_path), "DB_PASSWORD", "--requestor", "alice", "--reason", "rotation"],
    )
    assert result.exit_code == 0
    assert "DB_PASSWORD" in result.output
    assert "alice" in result.output
    assert "pending" in result.output


def test_approve_prints_confirmation(runner, vault_path):
    runner.invoke(
        approvals_group,
        ["request", str(vault_path), "API_KEY", "--requestor", "alice"],
    )
    result = runner.invoke(
        approvals_group,
        ["approve", str(vault_path), "API_KEY", "--reviewer", "bob"],
    )
    assert result.exit_code == 0
    assert "approved" in result.output
    assert "bob" in result.output


def test_reject_prints_confirmation(runner, vault_path):
    runner.invoke(
        approvals_group,
        ["request", str(vault_path), "TOKEN", "--requestor", "alice"],
    )
    result = runner.invoke(
        approvals_group,
        ["reject", str(vault_path), "TOKEN", "--reviewer", "carol"],
    )
    assert result.exit_code == 0
    assert "rejected" in result.output


def test_approve_unknown_key_exits_nonzero(runner, vault_path):
    result = runner.invoke(
        approvals_group,
        ["approve", str(vault_path), "MISSING", "--reviewer", "bob"],
    )
    assert result.exit_code != 0


def test_show_existing_approval(runner, vault_path):
    runner.invoke(
        approvals_group,
        ["request", str(vault_path), "SECRET", "--requestor", "alice", "--reason", "test"],
    )
    result = runner.invoke(approvals_group, ["show", str(vault_path), "SECRET"])
    assert result.exit_code == 0
    assert "pending" in result.output
    assert "alice" in result.output


def test_show_missing_key_says_no_record(runner, vault_path):
    result = runner.invoke(approvals_group, ["show", str(vault_path), "NOPE"])
    assert result.exit_code == 0
    assert "No approval record" in result.output


def test_list_pending_only(runner, vault_path):
    runner.invoke(approvals_group, ["request", str(vault_path), "A", "--requestor", "x"])
    runner.invoke(approvals_group, ["request", str(vault_path), "B", "--requestor", "y"])
    runner.invoke(approvals_group, ["approve", str(vault_path), "B", "--reviewer", "z"])
    result = runner.invoke(approvals_group, ["list", str(vault_path), "--pending"])
    assert "A" in result.output
    assert "B" not in result.output
