"""Tests for envault.scorecards."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import create_vault, update_vault
from envault.scorecards import (
    _scorecards_path,
    load_scorecards,
    compute_scorecards,
    get_scorecard,
    KeyScore,
)


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    p = tmp_path / "test.vault"
    create_vault(p, "secret", {"API_KEY": "abc123", "DB_URL": "postgres://localhost"})
    return p


def test_scorecards_path_is_sibling_of_vault(vault_path: Path) -> None:
    p = _scorecards_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.scorecards.json"


def test_load_scorecards_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_scorecards(vault_path) == {}


def test_compute_scorecards_returns_key_scores(vault_path: Path) -> None:
    results = compute_scorecards(vault_path, "secret")
    assert "API_KEY" in results
    assert "DB_URL" in results
    for ks in results.values():
        assert isinstance(ks, KeyScore)
        assert 0 <= ks.score <= 100


def test_compute_scorecards_persists_to_file(vault_path: Path) -> None:
    compute_scorecards(vault_path, "secret")
    stored = load_scorecards(vault_path)
    assert "API_KEY" in stored
    assert isinstance(stored["API_KEY"], int)


def test_healthy_key_scores_100(vault_path: Path) -> None:
    results = compute_scorecards(vault_path, "secret")
    assert results["API_KEY"].score == 100
    assert results["API_KEY"].reasons == []


def test_empty_value_penalises_score(vault_path: Path) -> None:
    update_vault(vault_path, "secret", {"API_KEY": ""})
    results = compute_scorecards(vault_path, "secret")
    assert results["API_KEY"].score <= 70
    assert "empty value" in results["API_KEY"].reasons


def test_placeholder_value_penalises_score(vault_path: Path) -> None:
    update_vault(vault_path, "secret", {"API_KEY": "changeme"})
    results = compute_scorecards(vault_path, "secret")
    assert results["API_KEY"].score <= 80
    assert "placeholder value" in results["API_KEY"].reasons


def test_get_scorecard_returns_none_when_not_computed(vault_path: Path) -> None:
    assert get_scorecard(vault_path, "API_KEY") is None


def test_get_scorecard_returns_value_after_compute(vault_path: Path) -> None:
    compute_scorecards(vault_path, "secret")
    score = get_scorecard(vault_path, "API_KEY")
    assert score is not None
    assert 0 <= score <= 100


def test_compute_scorecards_wrong_password_raises(vault_path: Path) -> None:
    with pytest.raises(ValueError):
        compute_scorecards(vault_path, "wrong")
