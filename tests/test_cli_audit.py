"""Tests for the audit CLI sub-commands."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.audit import record_event
from envault.cli_audit import audit_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_with_events(tmp_path: Path) -> str:
    p = tmp_path / "test.vault"
    p.touch()
    vault = str(p)
    record_event(vault, action="init", actor="bob")
    record_event(vault, action="set", key="API_KEY", actor="bob")
    record_event(vault, action="get", key="API_KEY", actor="alice")
    return vault


def test_log_shows_events(runner: CliRunner, vault_with_events: str) -> None:
    result = runner.invoke(audit_group, ["log", vault_with_events])
    assert result.exit_code == 0
    assert "init" in result.output
    assert "set" in result.output
    assert "API_KEY" in result.output


def test_log_filter_by_action(runner: CliRunner, vault_with_events: str) -> None:
    result = runner.invoke(audit_group, ["log", vault_with_events, "--action", "get"])
    assert result.exit_code == 0
    assert "get" in result.output
    assert "init" not in result.output


def test_log_last_limits_output(runner: CliRunner, vault_with_events: str) -> None:
    result = runner.invoke(audit_group, ["log", vault_with_events, "--last", "1"])
    assert result.exit_code == 0
    # Only the last event (get) should appear
    assert "get" in result.output
    assert result.output.count("\n") == 1


def test_log_empty_vault(runner: CliRunner, tmp_path: Path) -> None:
    p = tmp_path / "empty.vault"
    p.touch()
    result = runner.invoke(audit_group, ["log", str(p)])
    assert result.exit_code == 0
    assert "No audit events found" in result.output


def test_clear_log_removes_events(runner: CliRunner, vault_with_events: str) -> None:
    result = runner.invoke(audit_group, ["clear", vault_with_events], input="y\n")
    assert result.exit_code == 0
    assert "cleared" in result.output
    from envault.audit import read_events
    assert read_events(vault_with_events) == []


def test_clear_log_aborted(runner: CliRunner, vault_with_events: str) -> None:
    result = runner.invoke(audit_group, ["clear", vault_with_events], input="n\n")
    assert result.exit_code != 0 or "Aborted" in result.output
    from envault.audit import read_events
    assert len(read_events(vault_with_events)) == 3
