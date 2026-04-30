"""Tests for envault.retention."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from envault.retention import (
    _retention_path,
    get_retention,
    list_expired,
    load_retention,
    remove_retention,
    set_retention,
)
from envault.vault import create_vault


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(tmp_path / "test.vault", "secret", {"KEY": "value"})


def test_retention_path_is_sibling_of_vault(vault_path: Path) -> None:
    p = _retention_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.retention.json"


def test_load_retention_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_retention(vault_path) == {}


def test_set_retention_creates_entry(vault_path: Path) -> None:
    set_retention(vault_path, "KEY", 30, "days")
    data = load_retention(vault_path)
    assert "KEY" in data
    assert data["KEY"]["value"] == 30
    assert data["KEY"]["unit"] == "days"


def test_set_retention_returns_expiry_datetime(vault_path: Path) -> None:
    expires_at = set_retention(vault_path, "KEY", 7, "weeks")
    assert isinstance(expires_at, datetime)
    assert expires_at > datetime.utcnow()


def test_set_retention_invalid_unit_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid unit"):
        set_retention(vault_path, "KEY", 10, "minutes")  # type: ignore[arg-type]


def test_set_retention_non_positive_value_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        set_retention(vault_path, "KEY", 0, "days")


def test_get_retention_returns_entry(vault_path: Path) -> None:
    set_retention(vault_path, "KEY", 1, "years")
    entry = get_retention(vault_path, "KEY")
    assert entry is not None
    assert entry["unit"] == "years"


def test_get_retention_missing_key_returns_none(vault_path: Path) -> None:
    assert get_retention(vault_path, "MISSING") is None


def test_remove_retention_removes_key(vault_path: Path) -> None:
    set_retention(vault_path, "KEY", 30, "days")
    removed = remove_retention(vault_path, "KEY")
    assert removed is True
    assert get_retention(vault_path, "KEY") is None


def test_remove_retention_missing_key_returns_false(vault_path: Path) -> None:
    assert remove_retention(vault_path, "GHOST") is False


def test_list_expired_returns_elapsed_keys(vault_path: Path, monkeypatch) -> None:
    set_retention(vault_path, "OLD_KEY", 1, "days")
    # Manually backdate the expires_at so it appears expired
    import json
    from envault.retention import _retention_path
    p = _retention_path(vault_path)
    data = json.loads(p.read_text())
    data["OLD_KEY"]["expires_at"] = (datetime.utcnow() - timedelta(days=1)).isoformat()
    p.write_text(json.dumps(data))

    expired = list_expired(vault_path)
    assert "OLD_KEY" in expired


def test_list_expired_excludes_future_keys(vault_path: Path) -> None:
    set_retention(vault_path, "FRESH", 90, "days")
    assert "FRESH" not in list_expired(vault_path)
