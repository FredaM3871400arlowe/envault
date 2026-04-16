"""Tests for envault.tags."""
import pytest
from pathlib import Path
from envault.vault import create_vault
from envault.tags import (
    _tags_path, add_tag, remove_tag, get_tags, keys_with_tag, load_tags
)


@pytest.fixture
def vault_path(tmp_path):
    return create_vault(tmp_path / "test.vault", "pass")


def test_tags_path_is_sibling_of_vault(vault_path):
    tp = _tags_path(vault_path)
    assert tp.parent == vault_path.parent
    assert tp.name == "test.tags.json"


def test_load_tags_returns_empty_when_missing(vault_path):
    assert load_tags(vault_path) == {}


def test_add_tag_creates_entry(vault_path):
    add_tag(vault_path, "DB_URL", "database")
    assert "database" in get_tags(vault_path, "DB_URL")


def test_add_tag_no_duplicates(vault_path):
    add_tag(vault_path, "DB_URL", "database")
    add_tag(vault_path, "DB_URL", "database")
    assert get_tags(vault_path, "DB_URL").count("database") == 1


def test_add_multiple_tags(vault_path):
    add_tag(vault_path, "SECRET", "sensitive")
    add_tag(vault_path, "SECRET", "prod")
    tags = get_tags(vault_path, "SECRET")
    assert "sensitive" in tags
    assert "prod" in tags


def test_remove_tag(vault_path):
    add_tag(vault_path, "KEY", "mytag")
    remove_tag(vault_path, "KEY", "mytag")
    assert "mytag" not in get_tags(vault_path, "KEY")


def test_remove_tag_cleans_empty_key(vault_path):
    add_tag(vault_path, "KEY", "only")
    remove_tag(vault_path, "KEY", "only")
    assert "KEY" not in load_tags(vault_path)


def test_remove_unknown_tag_raises(vault_path):
    with pytest.raises(KeyError):
        remove_tag(vault_path, "KEY", "ghost")


def test_keys_with_tag(vault_path):
    add_tag(vault_path, "A", "prod")
    add_tag(vault_path, "B", "prod")
    add_tag(vault_path, "C", "dev")
    result = keys_with_tag(vault_path, "prod")
    assert set(result) == {"A", "B"}
