"""Tests for envault.annotations."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.annotations import (
    _annotations_path,
    load_annotations,
    set_annotation,
    get_annotation,
    remove_annotation,
    list_annotations,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "test.vault"


def test_annotations_path_is_sibling_of_vault(vault_path: Path) -> None:
    path = _annotations_path(vault_path)
    assert path.parent == vault_path.parent
    assert path.name == ".envault_annotations.json"


def test_load_annotations_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_annotations(vault_path) == {}


def test_set_and_get_annotation(vault_path: Path) -> None:
    set_annotation(vault_path, "DB_HOST", "Primary database hostname")
    result = get_annotation(vault_path, "DB_HOST")
    assert result == "Primary database hostname"


def test_get_annotation_missing_key_returns_none(vault_path: Path) -> None:
    assert get_annotation(vault_path, "MISSING_KEY") is None


def test_set_annotation_overwrites_existing(vault_path: Path) -> None:
    set_annotation(vault_path, "API_KEY", "Old note")
    set_annotation(vault_path, "API_KEY", "New note")
    assert get_annotation(vault_path, "API_KEY") == "New note"


def test_set_annotation_empty_key_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="key"):
        set_annotation(vault_path, "", "some text")


def test_set_annotation_empty_text_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="annotation text"):
        set_annotation(vault_path, "MY_KEY", "")


def test_remove_annotation_returns_true_when_present(vault_path: Path) -> None:
    set_annotation(vault_path, "TOKEN", "Auth token")
    assert remove_annotation(vault_path, "TOKEN") is True
    assert get_annotation(vault_path, "TOKEN") is None


def test_remove_annotation_returns_false_when_absent(vault_path: Path) -> None:
    assert remove_annotation(vault_path, "GHOST") is False


def test_list_annotations_returns_all(vault_path: Path) -> None:
    set_annotation(vault_path, "KEY_A", "Note A")
    set_annotation(vault_path, "KEY_B", "Note B")
    result = list_annotations(vault_path)
    assert result == {"KEY_A": "Note A", "KEY_B": "Note B"}


def test_annotations_persist_across_calls(vault_path: Path) -> None:
    set_annotation(vault_path, "PERSIST", "should survive")
    # Re-load from disk
    fresh = load_annotations(vault_path)
    assert fresh["PERSIST"] == "should survive"


def test_remove_does_not_affect_other_keys(vault_path: Path) -> None:
    set_annotation(vault_path, "KEEP", "keep me")
    set_annotation(vault_path, "DROP", "drop me")
    remove_annotation(vault_path, "DROP")
    assert get_annotation(vault_path, "KEEP") == "keep me"
    assert get_annotation(vault_path, "DROP") is None
