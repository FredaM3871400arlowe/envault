"""Tests for envault/signatures.py"""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import create_vault, update_vault
from envault.signatures import (
    _signatures_path,
    load_signatures,
    sign_key,
    verify_key,
    remove_signature,
    get_signature,
    list_signed_keys,
)

SECRET = "test-secret"
PASSWORD = "vault-pass"


@pytest.fixture
def vault_path(tmp_path) -> Path:
    p = tmp_path / "test.vault"
    create_vault(p, {"API_KEY": "abc123", "DB_URL": "postgres://localhost"}, PASSWORD)
    return p


def test_signatures_path_is_sibling_of_vault(vault_path):
    sig_path = _signatures_path(vault_path)
    assert sig_path.parent == vault_path.parent
    assert sig_path.name == "test.signatures.json"


def test_load_signatures_returns_empty_when_missing(vault_path):
    assert load_signatures(vault_path) == {}


def test_sign_key_creates_entry(vault_path):
    sign_key(vault_path, "API_KEY", "abc123", SECRET)
    sigs = load_signatures(vault_path)
    assert "API_KEY" in sigs
    assert isinstance(sigs["API_KEY"], str)
    assert len(sigs["API_KEY"]) == 64  # SHA-256 hex


def test_sign_key_persists(vault_path):
    sign_key(vault_path, "API_KEY", "abc123", SECRET)
    sigs = load_signatures(vault_path)
    sig = sigs["API_KEY"]
    reloaded = load_signatures(vault_path)
    assert reloaded["API_KEY"] == sig


def test_verify_key_returns_true_for_valid(vault_path):
    sign_key(vault_path, "API_KEY", "abc123", SECRET)
    assert verify_key(vault_path, "API_KEY", "abc123", SECRET) is True


def test_verify_key_returns_false_for_wrong_value(vault_path):
    sign_key(vault_path, "API_KEY", "abc123", SECRET)
    assert verify_key(vault_path, "API_KEY", "wrong-value", SECRET) is False


def test_verify_key_returns_false_for_wrong_secret(vault_path):
    sign_key(vault_path, "API_KEY", "abc123", SECRET)
    assert verify_key(vault_path, "API_KEY", "abc123", "wrong-secret") is False


def test_verify_key_returns_false_when_no_signature(vault_path):
    assert verify_key(vault_path, "API_KEY", "abc123", SECRET) is False


def test_remove_signature_deletes_entry(vault_path):
    sign_key(vault_path, "API_KEY", "abc123", SECRET)
    remove_signature(vault_path, "API_KEY")
    assert get_signature(vault_path, "API_KEY") is None


def test_remove_signature_missing_key_is_noop(vault_path):
    remove_signature(vault_path, "NONEXISTENT")  # should not raise


def test_get_signature_returns_none_when_missing(vault_path):
    assert get_signature(vault_path, "DB_URL") is None


def test_list_signed_keys_returns_all(vault_path):
    sign_key(vault_path, "API_KEY", "abc123", SECRET)
    sign_key(vault_path, "DB_URL", "postgres://localhost", SECRET)
    keys = list_signed_keys(vault_path)
    assert set(keys) == {"API_KEY", "DB_URL"}


def test_different_secrets_produce_different_sigs(vault_path):
    sig1 = sign_key(vault_path, "API_KEY", "abc123", "secret-a")
    sig2 = sign_key(vault_path, "API_KEY", "abc123", "secret-b")
    assert sig1 != sig2
