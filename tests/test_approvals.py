"""Tests for envault.approvals module."""
import pytest
from pathlib import Path

from envault.vault import create_vault
from envault.approvals import (
    _approvals_path,
    load_approvals,
    request_approval,
    review_approval,
    get_approval,
    remove_approval,
    list_pending,
)


@pytest.fixture
def vault_path(tmp_path):
    return create_vault(tmp_path / "test.vault", "password")


def test_approvals_path_is_sibling_of_vault(vault_path):
    p = _approvals_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == vault_path.stem + ".approvals.json"


def test_load_approvals_returns_empty_when_missing(vault_path):
    assert load_approvals(vault_path) == {}


def test_request_approval_creates_entry(vault_path):
    entry = request_approval(vault_path, "DB_PASSWORD", "alice", "rotating secret")
    assert entry["state"] == "pending"
    assert entry["requestor"] == "alice"
    assert entry["reason"] == "rotating secret"
    assert entry["reviewed_by"] is None


def test_request_approval_persists(vault_path):
    request_approval(vault_path, "API_KEY", "bob")
    data = load_approvals(vault_path)
    assert "API_KEY" in data
    assert data["API_KEY"]["state"] == "pending"


def test_review_approval_approve(vault_path):
    request_approval(vault_path, "SECRET", "alice")
    entry = review_approval(vault_path, "SECRET", "bob", approve=True)
    assert entry["state"] == "approved"
    assert entry["reviewed_by"] == "bob"
    assert entry["reviewed_at"] is not None


def test_review_approval_reject(vault_path):
    request_approval(vault_path, "TOKEN", "alice")
    entry = review_approval(vault_path, "TOKEN", "carol", approve=False)
    assert entry["state"] == "rejected"
    assert entry["reviewed_by"] == "carol"


def test_review_approval_unknown_key_raises(vault_path):
    with pytest.raises(KeyError):
        review_approval(vault_path, "MISSING", "bob", approve=True)


def test_review_approval_already_reviewed_raises(vault_path):
    request_approval(vault_path, "KEY", "alice")
    review_approval(vault_path, "KEY", "bob", approve=True)
    with pytest.raises(ValueError):
        review_approval(vault_path, "KEY", "carol", approve=False)


def test_get_approval_returns_none_when_missing(vault_path):
    assert get_approval(vault_path, "NOPE") is None


def test_remove_approval_deletes_entry(vault_path):
    request_approval(vault_path, "DB_HOST", "alice")
    remove_approval(vault_path, "DB_HOST")
    assert get_approval(vault_path, "DB_HOST") is None


def test_list_pending_filters_correctly(vault_path):
    request_approval(vault_path, "KEY_A", "alice")
    request_approval(vault_path, "KEY_B", "bob")
    review_approval(vault_path, "KEY_B", "carol", approve=True)
    pending = list_pending(vault_path)
    assert "KEY_A" in pending
    assert "KEY_B" not in pending
