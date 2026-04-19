import pytest
from pathlib import Path
from envault.bookmarks import (
    _bookmarks_path, load_bookmarks, add_bookmark,
    remove_bookmark, resolve_bookmark, list_bookmarks,
)


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "test.vault"


def test_bookmarks_path_is_sibling_of_vault(vault_path):
    bp = _bookmarks_path(vault_path)
    assert bp.parent == vault_path.parent
    assert bp.name == "test.bookmarks.json"


def test_load_bookmarks_returns_empty_when_missing(vault_path):
    assert load_bookmarks(vault_path) == {}


def test_add_bookmark_creates_entry(vault_path):
    add_bookmark(vault_path, "db", "DATABASE_URL")
    bm = load_bookmarks(vault_path)
    assert bm["db"] == "DATABASE_URL"


def test_add_bookmark_overwrites_existing(vault_path):
    add_bookmark(vault_path, "db", "DATABASE_URL")
    add_bookmark(vault_path, "db", "POSTGRES_URL")
    assert load_bookmarks(vault_path)["db"] == "POSTGRES_URL"


def test_add_bookmark_empty_name_raises(vault_path):
    with pytest.raises(ValueError):
        add_bookmark(vault_path, "", "SOME_KEY")


def test_add_bookmark_empty_key_raises(vault_path):
    with pytest.raises(ValueError):
        add_bookmark(vault_path, "mybook", "")


def test_remove_bookmark_deletes_entry(vault_path):
    add_bookmark(vault_path, "db", "DATABASE_URL")
    remove_bookmark(vault_path, "db")
    assert "db" not in load_bookmarks(vault_path)


def test_remove_unknown_bookmark_raises(vault_path):
    with pytest.raises(KeyError):
        remove_bookmark(vault_path, "nonexistent")


def test_resolve_bookmark_returns_key(vault_path):
    add_bookmark(vault_path, "secret", "SECRET_KEY")
    assert resolve_bookmark(vault_path, "secret") == "SECRET_KEY"


def test_resolve_missing_bookmark_raises(vault_path):
    with pytest.raises(KeyError):
        resolve_bookmark(vault_path, "ghost")


def test_list_bookmarks_returns_all(vault_path):
    add_bookmark(vault_path, "a", "KEY_A")
    add_bookmark(vault_path, "b", "KEY_B")
    result = list_bookmarks(vault_path)
    assert result == {"a": "KEY_A", "b": "KEY_B"}
