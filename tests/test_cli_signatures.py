"""Tests for envault/cli_signatures.py"""
from __future__ import annotations

import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.vault import create_vault
from envault.cli_signatures import signatures_group
from envault.signatures import sign_key, get_signature

PASSWORD = "vault-pass"
SECRET = "test-secret"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_path(tmp_path) -> Path:
    p = tmp_path / "test.vault"
    create_vault(p, {"API_KEY": "abc123", "DB_URL": "postgres://localhost"}, PASSWORD)
    return p


def test_sign_prints_confirmation(runner, vault_path):
    result = runner.invoke(
        signatures_group,
        ["sign", str(vault_path), "API_KEY",
         "--password", PASSWORD, "--secret", SECRET],
    )
    assert result.exit_code == 0
    assert "Signed 'API_KEY'" in result.output


def test_sign_unknown_key_exits_nonzero(runner, vault_path):
    result = runner.invoke(
        signatures_group,
        ["sign", str(vault_path), "MISSING_KEY",
         "--password", PASSWORD, "--secret", SECRET],
    )
    assert result.exit_code != 0


def test_verify_passes_for_signed_key(runner, vault_path):
    sign_key(vault_path, "API_KEY", "abc123", SECRET)
    result = runner.invoke(
        signatures_group,
        ["verify", str(vault_path), "API_KEY",
         "--password", PASSWORD, "--secret", SECRET],
    )
    assert result.exit_code == 0
    assert "OK" in result.output


def test_verify_fails_for_wrong_secret(runner, vault_path):
    sign_key(vault_path, "API_KEY", "abc123", SECRET)
    result = runner.invoke(
        signatures_group,
        ["verify", str(vault_path), "API_KEY",
         "--password", PASSWORD, "--secret", "wrong-secret"],
    )
    assert result.exit_code != 0
    assert "FAIL" in result.output


def test_remove_prints_confirmation(runner, vault_path):
    sign_key(vault_path, "API_KEY", "abc123", SECRET)
    result = runner.invoke(
        signatures_group,
        ["remove", str(vault_path), "API_KEY"],
    )
    assert result.exit_code == 0
    assert "Removed" in result.output
    assert get_signature(vault_path, "API_KEY") is None


def test_show_existing_signature(runner, vault_path):
    sign_key(vault_path, "DB_URL", "postgres://localhost", SECRET)
    result = runner.invoke(
        signatures_group,
        ["show", str(vault_path), "DB_URL"],
    )
    assert result.exit_code == 0
    assert "DB_URL" in result.output


def test_show_missing_signature(runner, vault_path):
    result = runner.invoke(
        signatures_group,
        ["show", str(vault_path), "API_KEY"],
    )
    assert result.exit_code == 0
    assert "No signature" in result.output


def test_list_shows_signed_keys(runner, vault_path):
    sign_key(vault_path, "API_KEY", "abc123", SECRET)
    sign_key(vault_path, "DB_URL", "postgres://localhost", SECRET)
    result = runner.invoke(signatures_group, ["list", str(vault_path)])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "DB_URL" in result.output
