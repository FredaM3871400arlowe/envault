"""Tests for envault.lifecycle."""
from __future__ import annotations

import pytest

from envault.lifecycle import (
    _lifecycle_path,
    get_state,
    list_by_state,
    load_lifecycle,
    remove_state,
    set_state,
)
from envault.vault import create_vault


@pytest.fixture()
def vault_path(tmp_path):
    p = create_vault(str(tmp_path / "test.vault"), "password")
    return str(p)


def test_lifecycle_path_is_sibling_of_vault(vault_path):
    lp = _lifecycle_path(vault_path)
    assert lp.parent == pytest.importorskip("pathlib").Path(vault_path).parent
    assert lp.name.endswith(".lifecycle.json")


def test_load_lifecycle_returns_empty_when_missing(vault_path):
    assert load_lifecycle(vault_path) == {}


def test_set_and_get_state(vault_path):
    set_state(vault_path, "MY_KEY", "draft")
    assert get_state(vault_path, "MY_KEY") == "draft"


def test_get_state_missing_key_returns_none(vault_path):
    assert get_state(vault_path, "MISSING") is None


def test_set_state_invalid_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid state"):
        set_state(vault_path, "K", "unknown")


def test_valid_transition_draft_to_active(vault_path):
    set_state(vault_path, "K", "draft")
    set_state(vault_path, "K", "active")
    assert get_state(vault_path, "K") == "active"


def test_invalid_transition_draft_to_archived_raises(vault_path):
    set_state(vault_path, "K", "draft")
    with pytest.raises(ValueError, match="Cannot transition"):
        set_state(vault_path, "K", "archived")


def test_archived_state_has_no_transitions(vault_path):
    set_state(vault_path, "K", "draft")
    set_state(vault_path, "K", "active")
    set_state(vault_path, "K", "archived")
    with pytest.raises(ValueError, match="Cannot transition"):
        set_state(vault_path, "K", "active")


def test_remove_state(vault_path):
    set_state(vault_path, "K", "draft")
    remove_state(vault_path, "K")
    assert get_state(vault_path, "K") is None


def test_remove_state_missing_key_is_noop(vault_path):
    remove_state(vault_path, "NONEXISTENT")  # should not raise


def test_list_by_state(vault_path):
    set_state(vault_path, "A", "draft")
    set_state(vault_path, "B", "draft")
    set_state(vault_path, "B", "active")
    assert set(list_by_state(vault_path, "draft")) == {"A"}
    assert set(list_by_state(vault_path, "active")) == {"B"}


def test_list_by_state_invalid_raises(vault_path):
    with pytest.raises(ValueError, match="Invalid state"):
        list_by_state(vault_path, "bogus")
