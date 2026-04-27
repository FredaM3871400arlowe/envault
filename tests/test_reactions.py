"""Tests for envault/reactions.py"""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.reactions import (
    VALID_REACTIONS,
    _reactions_path,
    add_reaction,
    clear_reactions,
    get_reactions,
    load_reactions,
    remove_reaction,
)
from envault.vault import create_vault


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(tmp_path / "test.vault", "password", {})


def test_reactions_path_is_sibling_of_vault(vault_path: Path) -> None:
    p = _reactions_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.reactions.json"


def test_load_reactions_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_reactions(vault_path) == {}


def test_add_reaction_creates_entry(vault_path: Path) -> None:
    result = add_reaction(vault_path, "MY_KEY", "👍")
    assert "👍" in result


def test_add_reaction_no_duplicates(vault_path: Path) -> None:
    add_reaction(vault_path, "MY_KEY", "👍")
    result = add_reaction(vault_path, "MY_KEY", "👍")
    assert result.count("👍") == 1


def test_add_reaction_invalid_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid reaction"):
        add_reaction(vault_path, "MY_KEY", "💩")


def test_add_multiple_reactions(vault_path: Path) -> None:
    add_reaction(vault_path, "MY_KEY", "👍")
    result = add_reaction(vault_path, "MY_KEY", "🔥")
    assert "👍" in result
    assert "🔥" in result


def test_get_reactions_returns_list(vault_path: Path) -> None:
    add_reaction(vault_path, "MY_KEY", "✅")
    assert get_reactions(vault_path, "MY_KEY") == ["✅"]


def test_get_reactions_missing_key_returns_empty(vault_path: Path) -> None:
    assert get_reactions(vault_path, "MISSING") == []


def test_remove_reaction(vault_path: Path) -> None:
    add_reaction(vault_path, "MY_KEY", "👍")
    add_reaction(vault_path, "MY_KEY", "❌")
    result = remove_reaction(vault_path, "MY_KEY", "👍")
    assert "👍" not in result
    assert "❌" in result


def test_remove_last_reaction_clears_key(vault_path: Path) -> None:
    add_reaction(vault_path, "MY_KEY", "👍")
    remove_reaction(vault_path, "MY_KEY", "👍")
    data = load_reactions(vault_path)
    assert "MY_KEY" not in data


def test_clear_reactions(vault_path: Path) -> None:
    add_reaction(vault_path, "MY_KEY", "👍")
    add_reaction(vault_path, "MY_KEY", "🔥")
    clear_reactions(vault_path, "MY_KEY")
    assert get_reactions(vault_path, "MY_KEY") == []


def test_valid_reactions_set_not_empty() -> None:
    assert len(VALID_REACTIONS) >= 5
