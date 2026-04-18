"""Integration tests: TTL interacts correctly with vault keys."""

from __future__ import annotations

import time

import pytest
from click.testing import CliRunner

from envault.vault import create_vault, update_vault, read_vault
from envault.ttl import set_ttl, list_expired, purge_expired
from envault.cli_ttl import ttl_group

PASSWORD = "s3cr3t"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def populated_vault(tmp_path):
    vp = create_vault(tmp_path / "int.vault", PASSWORD)
    update_vault(vp, PASSWORD, {"API_KEY": "abc123", "DB_PASS": "letmein"})
    return vp


def test_ttl_does_not_delete_vault_key_automatically(populated_vault):
    """TTL module tracks expiry metadata but does NOT mutate the vault itself."""
    set_ttl(populated_vault, "API_KEY", 1)
    time.sleep(1.1)
    data = read_vault(populated_vault, PASSWORD)
    # Key still present — purge must be called explicitly
    assert "API_KEY" in data


def test_purge_expired_only_removes_ttl_metadata(populated_vault):
    set_ttl(populated_vault, "DB_PASS", 1)
    time.sleep(1.1)
    purged = purge_expired(populated_vault)
    assert "DB_PASS" in purged
    # Vault data untouched
    data = read_vault(populated_vault, PASSWORD)
    assert "DB_PASS" in data


def test_multiple_keys_different_ttls(populated_vault):
    set_ttl(populated_vault, "API_KEY", 1)
    set_ttl(populated_vault, "DB_PASS", 9999)
    time.sleep(1.1)
    expired = list_expired(populated_vault)
    assert "API_KEY" in expired
    assert "DB_PASS" not in expired


def test_cli_purge_nothing_to_purge(runner, populated_vault):
    result = runner.invoke(ttl_group, ["purge", str(populated_vault)])
    assert result.exit_code == 0
    assert "Nothing" in result.output
