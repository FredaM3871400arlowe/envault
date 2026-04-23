"""Tests for envault/checksums.py"""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import create_vault
from envault.checksums import (
    _checksums_path,
    load_checksums,
    record_checksum,
    remove_checksum,
    verify_checksum,
    verify_all,
)

PASSWORD = "test-pass"


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    return create_vault(str(tmp_path / "test"), PASSWORD, {"KEY": "value"})


def test_checksums_path_is_sibling_of_vault(vault_path: Path) -> None:
    cp = _checksums_path(vault_path)
    assert cp.parent == vault_path.parent
    assert cp.name.endswith(".checksums.json")


def test_load_checksums_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_checksums(vault_path) == {}


def test_record_checksum_creates_entry(vault_path: Path) -> None:
    digest = record_checksum(vault_path, "KEY", "value")
    data = load_checksums(vault_path)
    assert "KEY" in data
    assert data["KEY"] == digest
    assert len(digest) == 64  # sha256 hex


def test_record_checksum_persists(vault_path: Path) -> None:
    record_checksum(vault_path, "KEY", "value")
    data = load_checksums(vault_path)
    assert "KEY" in data


def test_verify_checksum_correct_value(vault_path: Path) -> None:
    record_checksum(vault_path, "KEY", "value")
    assert verify_checksum(vault_path, "KEY", "value") is True


def test_verify_checksum_wrong_value(vault_path: Path) -> None:
    record_checksum(vault_path, "KEY", "value")
    assert verify_checksum(vault_path, "KEY", "different") is False


def test_verify_checksum_missing_key_returns_false(vault_path: Path) -> None:
    assert verify_checksum(vault_path, "MISSING", "anything") is False


def test_remove_checksum_deletes_entry(vault_path: Path) -> None:
    record_checksum(vault_path, "KEY", "value")
    remove_checksum(vault_path, "KEY")
    assert load_checksums(vault_path) == {}


def test_remove_checksum_noop_when_absent(vault_path: Path) -> None:
    remove_checksum(vault_path, "NONEXISTENT")  # should not raise


def test_verify_all_returns_correct_results(vault_path: Path) -> None:
    record_checksum(vault_path, "A", "alpha")
    record_checksum(vault_path, "B", "beta")
    results = verify_all(vault_path, {"A": "alpha", "B": "wrong"})
    assert results["A"] is True
    assert results["B"] is False


def test_verify_all_empty_when_no_checksums(vault_path: Path) -> None:
    assert verify_all(vault_path, {"KEY": "value"}) == {}
