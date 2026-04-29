"""Tests for envault.classifications."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.classifications import (
    CLASSIFICATIONS,
    auto_classify,
    classify_key,
    get_classification,
    load_classifications,
    remove_classification,
    set_classification,
)
from envault.vault import create_vault


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(tmp_path / "test.vault", "pw", {})


def test_classifications_path_is_sibling_of_vault(vault_path: Path) -> None:
    from envault.classifications import _classifications_path
    p = _classifications_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name.endswith(".classifications.json")


def test_load_classifications_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_classifications(vault_path) == {}


def test_set_and_get_classification(vault_path: Path) -> None:
    set_classification(vault_path, "DB_PASSWORD", "secret")
    assert get_classification(vault_path, "DB_PASSWORD") == "secret"


def test_get_classification_missing_key_returns_none(vault_path: Path) -> None:
    assert get_classification(vault_path, "NONEXISTENT") is None


def test_set_invalid_classification_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid classification"):
        set_classification(vault_path, "MY_KEY", "banana")


def test_remove_classification(vault_path: Path) -> None:
    set_classification(vault_path, "API_KEY", "credential")
    remove_classification(vault_path, "API_KEY")
    assert get_classification(vault_path, "API_KEY") is None


def test_remove_nonexistent_key_is_noop(vault_path: Path) -> None:
    remove_classification(vault_path, "GHOST")
    assert load_classifications(vault_path) == {}


@pytest.mark.parametrize("key,expected", [
    ("DB_PASSWORD", "secret"),
    ("API_KEY", "credential"),
    ("AUTH_TOKEN", "token"),
    ("SERVICE_URL", "url"),
    ("ENABLE_FEATURE", "flag"),
    ("APP_NAME", "other"),
])
def test_classify_key_heuristics(key: str, expected: str) -> None:
    assert classify_key(key) == expected


def test_classify_key_url_value(vault_path: Path) -> None:
    assert classify_key("REDIS_DSN", "redis://localhost:6379") == "url"


def test_auto_classify_fills_missing(vault_path: Path) -> None:
    env = {"DB_PASSWORD": "s3cr3t", "APP_ENV": "production"}
    result = auto_classify(vault_path, env)
    assert result["DB_PASSWORD"] == "secret"
    assert result["APP_ENV"] == "other"


def test_auto_classify_does_not_overwrite_existing(vault_path: Path) -> None:
    set_classification(vault_path, "DB_PASSWORD", "config")
    auto_classify(vault_path, {"DB_PASSWORD": "s3cr3t"})
    assert get_classification(vault_path, "DB_PASSWORD") == "config"


def test_all_classifications_are_valid_strings() -> None:
    assert all(isinstance(c, str) for c in CLASSIFICATIONS)
