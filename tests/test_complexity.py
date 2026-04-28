"""Tests for envault.complexity."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.vault import create_vault, update_vault
from envault.complexity import (
    ComplexityScore,
    _complexity_path,
    _grade,
    _score_value,
    compute_complexity,
    get_complexity,
    load_complexity,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    p = tmp_path / "test.vault"
    create_vault(p, "secret")
    update_vault(p, "secret", {"SIMPLE": "abc", "STRONG": "P@ssw0rd!XyZ99"})
    return p


# ---------------------------------------------------------------------------
# path helper
# ---------------------------------------------------------------------------

def test_complexity_path_is_sibling_of_vault(vault_path: Path) -> None:
    cp = _complexity_path(vault_path)
    assert cp.parent == vault_path.parent
    assert cp.name.endswith(".complexity.json")


# ---------------------------------------------------------------------------
# _score_value
# ---------------------------------------------------------------------------

def test_score_empty_value_is_zero() -> None:
    score, reasons = _score_value("")
    assert score == 0
    assert "empty value" in reasons


def test_score_short_value_low() -> None:
    score, reasons = _score_value("abc")
    assert score < 50
    assert any("shorter" in r for r in reasons)


def test_score_strong_value_high() -> None:
    score, reasons = _score_value("P@ssw0rd!XyZ99")
    assert score >= 80
    assert reasons == []


def test_score_no_special_chars_penalised() -> None:
    score, reasons = _score_value("Password1234")
    assert any("special" in r for r in reasons)


def test_score_repeated_chars_penalised() -> None:
    score, reasons = _score_value("aaaa1A!bbb")
    assert any("repeated" in r for r in reasons)


# ---------------------------------------------------------------------------
# _grade
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("score,expected", [
    (95, "A"), (80, "B"), (65, "C"), (45, "D"), (20, "F"),
])
def test_grade_boundaries(score: int, expected: str) -> None:
    assert _grade(score) == expected


# ---------------------------------------------------------------------------
# compute_complexity
# ---------------------------------------------------------------------------

def test_compute_complexity_returns_scores(vault_path: Path) -> None:
    results = compute_complexity(vault_path, "secret")
    keys = {r.key for r in results}
    assert "SIMPLE" in keys
    assert "STRONG" in keys


def test_compute_complexity_persists_to_file(vault_path: Path) -> None:
    compute_complexity(vault_path, "secret")
    data = load_complexity(vault_path)
    assert "SIMPLE" in data
    assert "score" in data["SIMPLE"]


def test_compute_complexity_strong_beats_simple(vault_path: Path) -> None:
    results = compute_complexity(vault_path, "secret")
    by_key = {r.key: r for r in results}
    assert by_key["STRONG"].score > by_key["SIMPLE"].score


# ---------------------------------------------------------------------------
# get_complexity
# ---------------------------------------------------------------------------

def test_get_complexity_returns_none_when_missing(vault_path: Path) -> None:
    assert get_complexity(vault_path, "NONEXISTENT") is None


def test_get_complexity_after_compute(vault_path: Path) -> None:
    compute_complexity(vault_path, "secret")
    result = get_complexity(vault_path, "SIMPLE")
    assert isinstance(result, ComplexityScore)
    assert result.key == "SIMPLE"


def test_load_complexity_returns_empty_when_missing(tmp_path: Path) -> None:
    fake = tmp_path / "ghost.vault"
    assert load_complexity(fake) == {}
