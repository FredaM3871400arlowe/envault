"""Tests for envault/favorites.py."""
import pytest
from pathlib import Path
from envault.favorites import (
    _favorites_path,
    add_favorite,
    remove_favorite,
    list_favorites,
    load_favorites,
)


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "test.vault"


def test_favorites_path_is_sibling_of_vault(vault_path):
    fp = _favorites_path(vault_path)
    assert fp.parent == vault_path.parent
    assert fp.name == "test.favorites.json"


def test_load_favorites_returns_empty_when_missing(vault_path):
    assert load_favorites(vault_path) == []


def test_add_favorite_creates_entry(vault_path):
    favs = add_favorite(vault_path, "DB_PASSWORD")
    assert "DB_PASSWORD" in favs


def test_add_favorite_no_duplicates(vault_path):
    add_favorite(vault_path, "API_KEY")
    favs = add_favorite(vault_path, "API_KEY")
    assert favs.count("API_KEY") == 1


def test_add_favorite_empty_key_raises(vault_path):
    with pytest.raises(ValueError):
        add_favorite(vault_path, "")


def test_remove_favorite_removes_entry(vault_path):
    add_favorite(vault_path, "SECRET")
    favs = remove_favorite(vault_path, "SECRET")
    assert "SECRET" not in favs


def test_remove_unknown_favorite_raises(vault_path):
    with pytest.raises(KeyError):
        remove_favorite(vault_path, "NONEXISTENT")


def test_list_favorites_returns_all(vault_path):
    add_favorite(vault_path, "KEY_A")
    add_favorite(vault_path, "KEY_B")
    favs = list_favorites(vault_path)
    assert "KEY_A" in favs
    assert "KEY_B" in favs


def test_favorites_persists_across_calls(vault_path):
    add_favorite(vault_path, "PERSIST_KEY")
    reloaded = load_favorites(vault_path)
    assert "PERSIST_KEY" in reloaded
