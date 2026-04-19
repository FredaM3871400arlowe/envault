"""Tests for envault.mentions."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import create_vault
from envault.mentions import (
    _mentions_path,
    load_mentions,
    scan_files,
    get_mentions,
    clear_mentions,
)

PASSWORD = "test-pass"


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(str(tmp_path / "test.vault"), {"DB_HOST": "localhost", "API_KEY": "secret"}, PASSWORD)


def test_mentions_path_is_sibling_of_vault(vault_path: Path) -> None:
    mp = _mentions_path(vault_path)
    assert mp.parent == vault_path.parent
    assert mp.name == "test.mentions.json"


def test_load_mentions_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_mentions(vault_path) == {}


def test_scan_files_detects_key(vault_path: Path, tmp_path: Path) -> None:
    src = tmp_path / "app.py"
    src.write_text("os.environ['DB_HOST']")
    results = scan_files(vault_path, [src], ["DB_HOST", "API_KEY"])
    assert str(src) in results["DB_HOST"]
    assert results["API_KEY"] == []


def test_scan_files_multiple_files(vault_path: Path, tmp_path: Path) -> None:
    f1 = tmp_path / "a.py"
    f2 = tmp_path / "b.py"
    f1.write_text("API_KEY = os.getenv('API_KEY')")
    f2.write_text("DB_HOST is used here")
    results = scan_files(vault_path, [f1, f2], ["API_KEY", "DB_HOST"])
    assert str(f1) in results["API_KEY"]
    assert str(f2) in results["DB_HOST"]


def test_scan_files_persists(vault_path: Path, tmp_path: Path) -> None:
    src = tmp_path / "cfg.py"
    src.write_text("DB_HOST")
    scan_files(vault_path, [src], ["DB_HOST"])
    loaded = load_mentions(vault_path)
    assert "DB_HOST" in loaded


def test_get_mentions_returns_list(vault_path: Path, tmp_path: Path) -> None:
    src = tmp_path / "x.py"
    src.write_text("DB_HOST")
    scan_files(vault_path, [src], ["DB_HOST"])
    assert get_mentions(vault_path, "DB_HOST") == [str(src)]


def test_get_mentions_missing_key_returns_empty(vault_path: Path) -> None:
    assert get_mentions(vault_path, "NONEXISTENT") == []


def test_clear_mentions_removes_file(vault_path: Path, tmp_path: Path) -> None:
    src = tmp_path / "z.py"
    src.write_text("DB_HOST")
    scan_files(vault_path, [src], ["DB_HOST"])
    assert _mentions_path(vault_path).exists()
    clear_mentions(vault_path)
    assert not _mentions_path(vault_path).exists()


def test_scan_overwrite_false_merges(vault_path: Path, tmp_path: Path) -> None:
    f1 = tmp_path / "a.py"
    f2 = tmp_path / "b.py"
    f1.write_text("DB_HOST")
    f2.write_text("API_KEY")
    scan_files(vault_path, [f1], ["DB_HOST"])
    scan_files(vault_path, [f2], ["API_KEY"], overwrite=False)
    data = load_mentions(vault_path)
    assert "DB_HOST" in data
    assert "API_KEY" in data
