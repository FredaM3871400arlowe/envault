"""Tests for envault.ratings."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import create_vault
from envault.ratings import (
    _ratings_path,
    load_ratings,
    set_rating,
    get_rating,
    remove_rating,
    list_ratings,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(str(tmp_path / "test.vault"), "password")


def test_ratings_path_is_sibling_of_vault(vault_path: Path) -> None:
    p = _ratings_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == ".envault_ratings.json"


def test_load_ratings_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_ratings(vault_path) == {}


def test_set_and_get_rating(vault_path: Path) -> None:
    set_rating(vault_path, "API_KEY", 5)
    assert get_rating(vault_path, "API_KEY") == 5


def test_get_rating_missing_key_returns_none(vault_path: Path) -> None:
    assert get_rating(vault_path, "MISSING") is None


def test_set_rating_invalid_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
        set_rating(vault_path, "KEY", 0)
    with pytest.raises(ValueError):
        set_rating(vault_path, "KEY", 6)


def test_set_rating_overwrites(vault_path: Path) -> None:
    set_rating(vault_path, "DB_URL", 3)
    set_rating(vault_path, "DB_URL", 1)
    assert get_rating(vault_path, "DB_URL") == 1


def test_remove_rating(vault_path: Path) -> None:
    set_rating(vault_path, "TOKEN", 4)
    remove_rating(vault_path, "TOKEN")
    assert get_rating(vault_path, "TOKEN") is None


def test_remove_rating_nonexistent_is_safe(vault_path: Path) -> None:
    remove_rating(vault_path, "GHOST")  # should not raise


def test_list_ratings(vault_path: Path) -> None:
    set_rating(vault_path, "A", 2)
    set_rating(vault_path, "B", 5)
    result = list_ratings(vault_path)
    assert result == {"A": 2, "B": 5}


def test_ratings_persist(vault_path: Path) -> None:
    set_rating(vault_path, "PERSIST_KEY", 3)
    reloaded = load_ratings(vault_path)
    assert reloaded["PERSIST_KEY"] == 3
