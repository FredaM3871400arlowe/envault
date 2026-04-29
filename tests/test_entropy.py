"""Tests for envault.entropy."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import create_vault, update_vault
from envault.entropy import (
    _entropy_path,
    load_entropy,
    compute_entropy,
    get_entropy,
    format_results,
    _calculate_entropy,
    _grade,
)


@pytest.fixture
def vault_path(tmp_path) -> Path:
    p = tmp_path / "test.vault"
    create_vault(p, "secret")
    update_vault(p, "secret", "API_KEY", "aB3$xZ9!qW2#mN7@")
    update_vault(p, "secret", "DEBUG", "true")
    update_vault(p, "secret", "EMPTY_VAL", "")
    return p


def test_entropy_path_is_sibling_of_vault(vault_path):
    ep = _entropy_path(vault_path)
    assert ep.parent == vault_path.parent
    assert ep.name == "test.entropy.json"


def test_load_entropy_returns_empty_when_missing(tmp_path):
    result = load_entropy(tmp_path / "nonexistent.vault")
    assert result == {}


def test_calculate_entropy_empty_string():
    assert _calculate_entropy("") == 0.0


def test_calculate_entropy_single_char():
    assert _calculate_entropy("aaaa") == 0.0


def test_calculate_entropy_uniform():
    # "ab" repeated — two equally likely chars → entropy = 1.0
    e = _calculate_entropy("ababab")
    assert abs(e - 1.0) < 1e-9


def test_grade_high():
    assert _grade(3.5) == "high"
    assert _grade(4.2) == "high"


def test_grade_medium():
    assert _grade(2.0) == "medium"
    assert _grade(3.4) == "medium"


def test_grade_low():
    assert _grade(0.0) == "low"
    assert _grade(1.9) == "low"


def test_compute_entropy_returns_results(vault_path):
    results = compute_entropy(vault_path, "secret")
    keys = [r.key for r in results]
    assert "API_KEY" in keys
    assert "DEBUG" in keys
    assert "EMPTY_VAL" in keys


def test_compute_entropy_persists_to_file(vault_path):
    compute_entropy(vault_path, "secret")
    data = load_entropy(vault_path)
    assert "API_KEY" in data
    assert "entropy" in data["API_KEY"]
    assert "grade" in data["API_KEY"]


def test_compute_entropy_high_entropy_value(vault_path):
    results = compute_entropy(vault_path, "secret")
    api = next(r for r in results if r.key == "API_KEY")
    assert api.grade == "high"
    assert api.entropy > 3.0


def test_compute_entropy_empty_value_is_zero(vault_path):
    results = compute_entropy(vault_path, "secret")
    empty = next(r for r in results if r.key == "EMPTY_VAL")
    assert empty.entropy == 0.0
    assert empty.grade == "low"


def test_get_entropy_returns_result(vault_path):
    compute_entropy(vault_path, "secret")
    result = get_entropy(vault_path, "DEBUG")
    assert result is not None
    assert result.key == "DEBUG"


def test_get_entropy_missing_key_returns_none(vault_path):
    compute_entropy(vault_path, "secret")
    assert get_entropy(vault_path, "NONEXISTENT") is None


def test_format_results_contains_keys(vault_path):
    results = compute_entropy(vault_path, "secret")
    output = format_results(results)
    assert "API_KEY" in output
    assert "DEBUG" in output
    assert "GRADE" in output
