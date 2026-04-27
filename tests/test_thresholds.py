"""Tests for envault/thresholds.py and envault/cli_thresholds.py."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.thresholds import (
    _thresholds_path,
    check_threshold,
    get_threshold,
    list_thresholds,
    remove_threshold,
    set_threshold,
)
from envault.cli_thresholds import thresholds_group
from envault.vault import create_vault


@pytest.fixture()
def vault_path(tmp_path):
    path = create_vault(str(tmp_path / "test.vault"), "password")
    return path


@pytest.fixture()
def runner():
    return CliRunner()


# --- unit tests ---

def test_thresholds_path_is_sibling_of_vault(vault_path):
    p = _thresholds_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == ".envault_thresholds.json"


def test_load_thresholds_returns_empty_when_missing(vault_path):
    assert list_thresholds(vault_path) == {}


def test_set_and_get_threshold(vault_path):
    set_threshold(vault_path, "PORT", "min", 1024)
    entry = get_threshold(vault_path, "PORT")
    assert entry == {"min": 1024}


def test_set_both_min_and_max(vault_path):
    set_threshold(vault_path, "TIMEOUT", "min", 0)
    set_threshold(vault_path, "TIMEOUT", "max", 300)
    entry = get_threshold(vault_path, "TIMEOUT")
    assert entry["min"] == 0
    assert entry["max"] == 300


def test_get_threshold_missing_key_returns_none(vault_path):
    assert get_threshold(vault_path, "MISSING") is None


def test_set_invalid_kind_raises(vault_path):
    with pytest.raises(ValueError, match="kind must be one of"):
        set_threshold(vault_path, "KEY", "exact", 42)


def test_remove_threshold(vault_path):
    set_threshold(vault_path, "KEY", "max", 100)
    remove_threshold(vault_path, "KEY")
    assert get_threshold(vault_path, "KEY") is None


def test_check_threshold_no_violation(vault_path):
    set_threshold(vault_path, "WORKERS", "min", 1)
    set_threshold(vault_path, "WORKERS", "max", 16)
    assert check_threshold(vault_path, "WORKERS", 8) == []


def test_check_threshold_min_violation(vault_path):
    set_threshold(vault_path, "WORKERS", "min", 1)
    violations = check_threshold(vault_path, "WORKERS", 0)
    assert len(violations) == 1
    assert "below minimum" in violations[0]


def test_check_threshold_max_violation(vault_path):
    set_threshold(vault_path, "WORKERS", "max", 16)
    violations = check_threshold(vault_path, "WORKERS", 32)
    assert "above maximum" in violations[0]


def test_check_threshold_no_threshold_returns_empty(vault_path):
    assert check_threshold(vault_path, "UNSET", 999) == []


# --- CLI tests ---

def test_set_prints_confirmation(runner, vault_path):
    result = runner.invoke(thresholds_group, ["set", str(vault_path), "PORT", "--min", "1024"])
    assert result.exit_code == 0
    assert "Threshold set" in result.output


def test_set_no_options_exits_nonzero(runner, vault_path):
    result = runner.invoke(thresholds_group, ["set", str(vault_path), "PORT"])
    assert result.exit_code != 0


def test_get_existing_threshold(runner, vault_path):
    set_threshold(vault_path, "PORT", "min", 80)
    result = runner.invoke(thresholds_group, ["get", str(vault_path), "PORT"])
    assert result.exit_code == 0
    assert "80" in result.output


def test_get_missing_threshold(runner, vault_path):
    result = runner.invoke(thresholds_group, ["get", str(vault_path), "NOKEY"])
    assert "No threshold" in result.output


def test_check_cmd_ok(runner, vault_path):
    set_threshold(vault_path, "PORT", "min", 1024)
    result = runner.invoke(thresholds_group, ["check", str(vault_path), "PORT", "8080"])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_check_cmd_violation_exits_nonzero(runner, vault_path):
    set_threshold(vault_path, "PORT", "min", 1024)
    result = runner.invoke(thresholds_group, ["check", str(vault_path), "PORT", "80"])
    assert result.exit_code != 0
