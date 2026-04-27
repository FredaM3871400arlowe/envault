"""Unit tests for envault.relationships."""

from pathlib import Path

import pytest

from envault.relationships import (
    _relationships_path,
    add_relationship,
    get_relationships,
    list_all_related_keys,
    load_relationships,
    remove_relationship,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "test.vault"


def test_relationships_path_is_sibling_of_vault(vault_path: Path) -> None:
    result = _relationships_path(vault_path)
    assert result.parent == vault_path.parent
    assert result.name == "test.relationships.json"


def test_load_relationships_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_relationships(vault_path) == {}


def test_add_relationship_creates_entry(vault_path: Path) -> None:
    add_relationship(vault_path, "DB_URL", "requires", "DB_PASS")
    rels = get_relationships(vault_path, "DB_URL")
    assert "requires" in rels
    assert "DB_PASS" in rels["requires"]


def test_add_relationship_no_duplicates(vault_path: Path) -> None:
    add_relationship(vault_path, "DB_URL", "requires", "DB_PASS")
    add_relationship(vault_path, "DB_URL", "requires", "DB_PASS")
    rels = get_relationships(vault_path, "DB_URL")
    assert rels["requires"].count("DB_PASS") == 1


def test_add_relationship_invalid_type_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="Unknown relationship type"):
        add_relationship(vault_path, "A", "owns", "B")


def test_add_relationship_self_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="itself"):
        add_relationship(vault_path, "A", "requires", "A")


def test_add_relationship_empty_key_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError):
        add_relationship(vault_path, "", "requires", "B")


def test_remove_relationship_returns_true_when_found(vault_path: Path) -> None:
    add_relationship(vault_path, "A", "conflicts", "B")
    removed = remove_relationship(vault_path, "A", "conflicts", "B")
    assert removed is True


def test_remove_relationship_returns_false_when_missing(vault_path: Path) -> None:
    removed = remove_relationship(vault_path, "A", "conflicts", "B")
    assert removed is False


def test_remove_relationship_cleans_up_empty_keys(vault_path: Path) -> None:
    add_relationship(vault_path, "A", "related", "B")
    remove_relationship(vault_path, "A", "related", "B")
    assert load_relationships(vault_path) == {}


def test_multiple_relationship_types_for_same_key(vault_path: Path) -> None:
    add_relationship(vault_path, "A", "requires", "B")
    add_relationship(vault_path, "A", "conflicts", "C")
    rels = get_relationships(vault_path, "A")
    assert "B" in rels["requires"]
    assert "C" in rels["conflicts"]


def test_list_all_related_keys(vault_path: Path) -> None:
    add_relationship(vault_path, "A", "requires", "B")
    add_relationship(vault_path, "X", "related", "Y")
    keys = list_all_related_keys(vault_path)
    assert "A" in keys
    assert "X" in keys
    assert "B" not in keys  # targets are not listed as sources
