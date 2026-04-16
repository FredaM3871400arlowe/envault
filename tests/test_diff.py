"""Tests for envault.diff."""

import pytest

from envault.diff import DiffResult, diff_dicts, diff_vault_vs_env, format_diff
from envault.vault import create_vault, update_vault


# ---------------------------------------------------------------------------
# diff_dicts
# ---------------------------------------------------------------------------

def test_diff_dicts_all_same():
    result = diff_dicts({"A": "1", "B": "2"}, {"A": "1", "B": "2"})
    assert result.added == []
    assert result.removed == []
    assert result.changed == []
    assert result.unchanged == ["A", "B"]
    assert not result.has_differences


def test_diff_dicts_added():
    result = diff_dicts({"A": "1", "NEW": "x"}, {"A": "1"})
    assert result.added == ["NEW"]
    assert result.removed == []


def test_diff_dicts_removed():
    result = diff_dicts({"A": "1"}, {"A": "1", "OLD": "z"})
    assert result.removed == ["OLD"]
    assert result.added == []


def test_diff_dicts_changed():
    result = diff_dicts({"A": "new"}, {"A": "old"})
    assert result.changed == ["A"]
    assert result.unchanged == []
    assert result.has_differences


def test_diff_dicts_mixed():
    vault = {"A": "1", "B": "changed", "C": "only_vault"}
    env = {"A": "1", "B": "original", "D": "only_env"}
    result = diff_dicts(vault, env)
    assert result.unchanged == ["A"]
    assert result.changed == ["B"]
    assert result.added == ["C"]
    assert result.removed == ["D"]


# ---------------------------------------------------------------------------
# format_diff
# ---------------------------------------------------------------------------

def test_format_diff_no_differences():
    result = DiffResult(added=[], removed=[], changed=[], unchanged=["X"])
    assert format_diff(result) == "No differences found."


def test_format_diff_shows_symbols():
    result = DiffResult(added=["NEW"], removed=["OLD"], changed=["MOD"], unchanged=[])
    output = format_diff(result)
    assert "+ NEW" in output
    assert "- OLD" in output
    assert "~ MOD" in output


# ---------------------------------------------------------------------------
# diff_vault_vs_env (integration)
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY1=hello\nKEY2=world\n")
    return str(env_file)


def test_diff_vault_vs_env_detects_added(tmp_path, tmp_env_file):
    vault_path = str(tmp_path / "test.vault")
    create_vault(vault_path, "pass", {"KEY1": "hello", "KEY2": "world", "EXTRA": "bonus"})
    result = diff_vault_vs_env(vault_path, "pass", tmp_env_file)
    assert "EXTRA" in result.added
    assert result.removed == []


def test_diff_vault_vs_env_detects_changed(tmp_path, tmp_env_file):
    vault_path = str(tmp_path / "test.vault")
    create_vault(vault_path, "pass", {"KEY1": "hello", "KEY2": "different"})
    result = diff_vault_vs_env(vault_path, "pass", tmp_env_file)
    assert "KEY2" in result.changed
