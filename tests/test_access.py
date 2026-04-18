"""Tests for envault.access module."""
import pytest
from pathlib import Path
from envault.access import (
    _access_path,
    load_access,
    grant,
    revoke,
    check,
    list_permissions,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "test.vault"


def test_access_path_is_sibling_of_vault(vault_path):
    ap = _access_path(vault_path)
    assert ap.parent == vault_path.parent
    assert ap.name == "test.access.json"


def test_load_access_returns_empty_when_missing(vault_path):
    assert load_access(vault_path) == {}


def test_grant_creates_entry(vault_path):
    grant(vault_path, "API_KEY", "read")
    data = load_access(vault_path)
    assert "API_KEY" in data
    assert "read" in data["API_KEY"]


def test_grant_invalid_permission_raises(vault_path):
    with pytest.raises(ValueError, match="Unknown permission"):
        grant(vault_path, "API_KEY", "execute")


def test_grant_no_duplicates(vault_path):
    grant(vault_path, "API_KEY", "read")
    grant(vault_path, "API_KEY", "read")
    data = load_access(vault_path)
    assert data["API_KEY"].count("read") == 1


def test_revoke_removes_permission(vault_path):
    grant(vault_path, "DB_PASS", "read")
    grant(vault_path, "DB_PASS", "write")
    revoke(vault_path, "DB_PASS", "write")
    data = load_access(vault_path)
    assert "write" not in data["DB_PASS"]
    assert "read" in data["DB_PASS"]


def test_revoke_last_permission_removes_key(vault_path):
    grant(vault_path, "TOKEN", "read")
    revoke(vault_path, "TOKEN", "read")
    data = load_access(vault_path)
    assert "TOKEN" not in data


def test_check_returns_true_when_no_rules(vault_path):
    assert check(vault_path, "ANYTHING", "read") is True


def test_check_returns_true_for_granted_permission(vault_path):
    grant(vault_path, "SECRET", "read")
    assert check(vault_path, "SECRET", "read") is True


def test_check_returns_false_for_missing_permission(vault_path):
    grant(vault_path, "SECRET", "read")
    assert check(vault_path, "SECRET", "write") is False


def test_list_permissions_returns_defaults_when_no_rules(vault_path):
    perms = list_permissions(vault_path, "UNSET_KEY")
    assert set(perms) == {"read", "write"}


def test_list_permissions_returns_granted(vault_path):
    grant(vault_path, "KEY", "read")
    assert list_permissions(vault_path, "KEY") == ["read"]
