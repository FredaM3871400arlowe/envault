"""Tests for envault.hooks."""
import pytest
from pathlib import Path
from envault.hooks import (
    _hooks_path, add_hook, remove_hook, load_hooks, run_hooks
)


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "test.vault"


def test_hooks_path_is_sibling_of_vault(vault_path):
    p = _hooks_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == ".envault-hooks.json"


def test_load_hooks_returns_empty_when_missing(vault_path):
    assert load_hooks(vault_path) == {}


def test_add_hook_creates_entry(vault_path):
    add_hook(vault_path, "post-set", "echo hello")
    hooks = load_hooks(vault_path)
    assert "post-set" in hooks
    assert "echo hello" in hooks["post-set"]


def test_add_hook_invalid_event_raises(vault_path):
    with pytest.raises(ValueError, match="Unknown event"):
        add_hook(vault_path, "on-magic", "echo hi")


def test_add_hook_no_duplicates(vault_path):
    add_hook(vault_path, "post-set", "echo hello")
    add_hook(vault_path, "post-set", "echo hello")
    hooks = load_hooks(vault_path)
    assert hooks["post-set"].count("echo hello") == 1


def test_remove_hook(vault_path):
    add_hook(vault_path, "pre-get", "echo before")
    remove_hook(vault_path, "pre-get", "echo before")
    hooks = load_hooks(vault_path)
    assert "echo before" not in hooks.get("pre-get", [])


def test_remove_nonexistent_hook_raises(vault_path):
    with pytest.raises(KeyError):
        remove_hook(vault_path, "pre-get", "echo nope")


def test_run_hooks_executes_command(vault_path):
    add_hook(vault_path, "post-export", "echo envault")
    outputs = run_hooks(vault_path, "post-export")
    assert outputs == ["envault"]


def test_run_hooks_failing_command_raises(vault_path):
    add_hook(vault_path, "pre-set", "exit 1")
    with pytest.raises(RuntimeError, match="Hook failed"):
        run_hooks(vault_path, "pre-set")


def test_run_hooks_no_hooks_returns_empty(vault_path):
    result = run_hooks(vault_path, "post-get")
    assert result == []
