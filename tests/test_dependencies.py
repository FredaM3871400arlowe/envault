"""Tests for envault.dependencies."""
import pytest
from pathlib import Path
from envault.dependencies import (
    _deps_path,
    add_dependency,
    remove_dependency,
    get_dependencies,
    get_dependents,
    clear_dependencies,
    load_dependencies,
)


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "test.vault"


def test_deps_path_is_sibling_of_vault(vault_path):
    p = _deps_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.deps.json"


def test_load_deps_returns_empty_when_missing(vault_path):
    assert load_dependencies(vault_path) == {}


def test_add_dependency_creates_entry(vault_path):
    add_dependency(vault_path, "DATABASE_URL", "DB_HOST")
    deps = get_dependencies(vault_path, "DATABASE_URL")
    assert "DB_HOST" in deps


def test_add_dependency_no_duplicates(vault_path):
    add_dependency(vault_path, "A", "B")
    add_dependency(vault_path, "A", "B")
    assert get_dependencies(vault_path, "A").count("B") == 1


def test_add_dependency_empty_key_raises(vault_path):
    with pytest.raises(ValueError):
        add_dependency(vault_path, "", "B")


def test_add_dependency_empty_depends_on_raises(vault_path):
    with pytest.raises(ValueError):
        add_dependency(vault_path, "A", "")


def test_add_dependency_self_raises(vault_path):
    with pytest.raises(ValueError):
        add_dependency(vault_path, "A", "A")


def test_remove_dependency(vault_path):
    add_dependency(vault_path, "A", "B")
    remove_dependency(vault_path, "A", "B")
    assert get_dependencies(vault_path, "A") == []


def test_remove_nonexistent_dependency_raises(vault_path):
    with pytest.raises(KeyError):
        remove_dependency(vault_path, "A", "B")


def test_get_dependents(vault_path):
    add_dependency(vault_path, "A", "C")
    add_dependency(vault_path, "B", "C")
    dependents = get_dependents(vault_path, "C")
    assert set(dependents) == {"A", "B"}


def test_clear_dependencies_removes_all(vault_path):
    add_dependency(vault_path, "A", "B")
    add_dependency(vault_path, "C", "A")
    clear_dependencies(vault_path, "A")
    assert get_dependencies(vault_path, "A") == []
    assert "A" not in get_dependents(vault_path, "B")
    assert get_dependents(vault_path, "A") == []
