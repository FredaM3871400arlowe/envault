"""Tests for envault/cli_ttl.py"""

from __future__ import annotations

import time

import pytest
from click.testing import CliRunner

from envault.vault import create_vault
from envault.cli_ttl import ttl_group

PASSWORD = "hunter2"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path):
    return create_vault(tmp_path / "v.vault", PASSWORD)


def test_set_prints_confirmation(runner, vault_path):
    result = runner.invoke(ttl_group, ["set", str(vault_path), "API_KEY", "3600"])
    assert result.exit_code == 0
    assert "expires at" in result.output


def test_set_invalid_seconds_exits_nonzero(runner, vault_path):
    result = runner.invoke(ttl_group, ["set", str(vault_path), "KEY", "0"])
    assert result.exit_code != 0


def test_show_existing_ttl(runner, vault_path):
    runner.invoke(ttl_group, ["set", str(vault_path), "MY_KEY", "7200"])
    result = runner.invoke(ttl_group, ["show", str(vault_path), "MY_KEY"])
    assert result.exit_code == 0
    assert "expires at" in result.output


def test_show_missing_ttl(runner, vault_path):
    result = runner.invoke(ttl_group, ["show", str(vault_path), "GHOST"])
    assert result.exit_code == 0
    assert "No TTL" in result.output


def test_clear_existing_ttl(runner, vault_path):
    runner.invoke(ttl_group, ["set", str(vault_path), "TMP", "60"])
    result = runner.invoke(ttl_group, ["clear", str(vault_path), "TMP"])
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_list_expired_shows_stale_key(runner, vault_path):
    runner.invoke(ttl_group, ["set", str(vault_path), "STALE", "1"])
    time.sleep(1.1)
    result = runner.invoke(ttl_group, ["list-expired", str(vault_path)])
    assert "STALE" in result.output


def test_purge_removes_expired(runner, vault_path):
    runner.invoke(ttl_group, ["set", str(vault_path), "OLD", "1"])
    time.sleep(1.1)
    result = runner.invoke(ttl_group, ["purge", str(vault_path)])
    assert "OLD" in result.output
    assert "Purged" in result.output
