"""Tests for envault.categories."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.vault import create_vault
from envault.categories import (
    _categories_path,
    load_categories,
    set_category,
    get_category,
    remove_category,
    list_by_category,
)
from envault.cli_categories import categories_group


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(tmp_path / "test.vault", "secret", {})


def test_categories_path_is_sibling_of_vault(vault_path: Path) -> None:
    p = _categories_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.categories.json"


def test_load_categories_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_categories(vault_path) == {}


def test_set_and_get_category(vault_path: Path) -> None:
    set_category(vault_path, "DB_URL", "database")
    assert get_category(vault_path, "DB_URL") == "database"


def test_get_category_missing_key_returns_none(vault_path: Path) -> None:
    assert get_category(vault_path, "MISSING") is None


def test_set_category_invalid_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid category"):
        set_category(vault_path, "KEY", "nonexistent")


def test_set_category_empty_key_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError, match="empty"):
        set_category(vault_path, "", "auth")


def test_remove_category_existing(vault_path: Path) -> None:
    set_category(vault_path, "API_KEY", "auth")
    result = remove_category(vault_path, "API_KEY")
    assert result is True
    assert get_category(vault_path, "API_KEY") is None


def test_remove_category_missing_returns_false(vault_path: Path) -> None:
    assert remove_category(vault_path, "GHOST") is False


def test_list_by_category(vault_path: Path) -> None:
    set_category(vault_path, "DB_URL", "database")
    set_category(vault_path, "DB_PASS", "database")
    set_category(vault_path, "LOG_LEVEL", "logging")
    db_keys = list_by_category(vault_path, "database")
    assert sorted(db_keys) == ["DB_PASS", "DB_URL"]
    assert list_by_category(vault_path, "logging") == ["LOG_LEVEL"]
    assert list_by_category(vault_path, "auth") == []


# --- CLI tests ---

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_set_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(categories_group, ["set", str(vault_path), "API_KEY", "auth"])
    assert result.exit_code == 0
    assert "auth" in result.output
    assert "API_KEY" in result.output


def test_get_existing_category(runner: CliRunner, vault_path: Path) -> None:
    set_category(vault_path, "S3_BUCKET", "storage")
    result = runner.invoke(categories_group, ["get", str(vault_path), "S3_BUCKET"])
    assert result.exit_code == 0
    assert "storage" in result.output


def test_get_missing_category(runner: CliRunner, vault_path: Path) -> None:
    result = runner.invoke(categories_group, ["get", str(vault_path), "UNKNOWN"])
    assert result.exit_code == 0
    assert "No category" in result.output


def test_remove_prints_confirmation(runner: CliRunner, vault_path: Path) -> None:
    set_category(vault_path, "REDIS_URL", "network")
    result = runner.invoke(categories_group, ["remove", str(vault_path), "REDIS_URL"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_list_shows_all(runner: CliRunner, vault_path: Path) -> None:
    set_category(vault_path, "DB_URL", "database")
    set_category(vault_path, "LOG_LEVEL", "logging")
    result = runner.invoke(categories_group, ["list", str(vault_path)])
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "LOG_LEVEL" in result.output


def test_list_filter_by_category(runner: CliRunner, vault_path: Path) -> None:
    set_category(vault_path, "DB_URL", "database")
    set_category(vault_path, "LOG_LEVEL", "logging")
    result = runner.invoke(categories_group, ["list", str(vault_path), "--filter", "database"])
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "LOG_LEVEL" not in result.output
