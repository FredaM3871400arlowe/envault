"""Tests for envault/constraints.py."""

from __future__ import annotations

import pytest

from envault.constraints import (
    _constraints_path,
    check_value,
    get_constraint,
    load_constraints,
    remove_constraint,
    set_constraint,
)
from envault.vault import create_vault


@pytest.fixture()
def vault_path(tmp_path):
    p = tmp_path / "test.vault"
    create_vault(str(p), "secret", {})
    return str(p)


def test_constraints_path_is_sibling_of_vault(vault_path):
    cp = _constraints_path(vault_path)
    assert cp.name == "test.constraints.json"
    assert cp.parent == cp.parent  # same directory


def test_load_constraints_returns_empty_when_missing(vault_path):
    assert load_constraints(vault_path) == {}


def test_set_and_get_constraint(vault_path):
    set_constraint(vault_path, "PORT", min_length=1, max_length=5)
    c = get_constraint(vault_path, "PORT")
    assert c == {"min_length": 1, "max_length": 5}


def test_get_constraint_missing_key_returns_none(vault_path):
    assert get_constraint(vault_path, "MISSING") is None


def test_set_constraint_with_pattern(vault_path):
    set_constraint(vault_path, "EMAIL", pattern=r"[^@]+@[^@]+\.[^@]+")
    c = get_constraint(vault_path, "EMAIL")
    assert c["pattern"] == r"[^@]+@[^@]+\.[^@]+"


def test_set_constraint_invalid_regex_raises(vault_path):
    with pytest.raises(Exception):
        set_constraint(vault_path, "KEY", pattern="[invalid")


def test_set_constraint_empty_key_raises(vault_path):
    with pytest.raises(ValueError):
        set_constraint(vault_path, "", pattern=".*")


def test_set_constraint_allowed_values(vault_path):
    set_constraint(vault_path, "ENV", allowed_values=["dev", "staging", "prod"])
    c = get_constraint(vault_path, "ENV")
    assert c["allowed_values"] == ["dev", "staging", "prod"]


def test_remove_constraint_returns_true(vault_path):
    set_constraint(vault_path, "KEY", min_length=1)
    assert remove_constraint(vault_path, "KEY") is True
    assert get_constraint(vault_path, "KEY") is None


def test_remove_constraint_missing_returns_false(vault_path):
    assert remove_constraint(vault_path, "NOPE") is False


def test_check_value_pattern_pass():
    assert check_value({"pattern": r"\d+"}, "123") == []


def test_check_value_pattern_fail():
    violations = check_value({"pattern": r"\d+"}, "abc")
    assert len(violations) == 1
    assert "pattern" in violations[0]


def test_check_value_min_length_fail():
    violations = check_value({"min_length": 5}, "hi")
    assert len(violations) == 1
    assert "minimum" in violations[0]


def test_check_value_max_length_fail():
    violations = check_value({"max_length": 3}, "toolong")
    assert len(violations) == 1
    assert "exceeds" in violations[0]


def test_check_value_allowed_values_pass():
    assert check_value({"allowed_values": ["a", "b"]}, "a") == []


def test_check_value_allowed_values_fail():
    violations = check_value({"allowed_values": ["a", "b"]}, "c")
    assert len(violations) == 1
    assert "allowed values" in violations[0]


def test_check_value_multiple_violations():
    violations = check_value({"min_length": 10, "pattern": r"\d+"}, "ab")
    assert len(violations) == 2
