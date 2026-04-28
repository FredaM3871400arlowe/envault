"""Tests for envault.confidence."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.confidence import (
    ConfidenceScore,
    _confidence_path,
    compute_confidence,
    get_confidence,
    load_confidence,
    save_confidence,
)
from envault.vault import create_vault

PASSWORD = "testpass"


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(tmp_path / "vault", PASSWORD, {"API_KEY": "abc", "DB_URL": "postgres://"})


def test_confidence_path_is_sibling_of_vault(vault_path: Path) -> None:
    p = _confidence_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name.endswith(".confidence.json")


def test_load_confidence_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_confidence(vault_path) == {}


def test_save_and_load_roundtrip(vault_path: Path) -> None:
    data = {"API_KEY": {"score": 50, "level": "medium", "reasons": ["has note"]}}
    save_confidence(vault_path, data)
    loaded = load_confidence(vault_path)
    assert loaded == data


def test_compute_confidence_returns_scores(vault_path: Path) -> None:
    results = compute_confidence(vault_path, ["API_KEY", "DB_URL"])
    assert "API_KEY" in results
    assert "DB_URL" in results
    for score in results.values():
        assert isinstance(score, ConfidenceScore)
        assert 0 <= score.score <= 100
        assert score.level in ("low", "medium", "high")


def test_compute_confidence_persists_to_file(vault_path: Path) -> None:
    compute_confidence(vault_path, ["API_KEY"])
    assert _confidence_path(vault_path).exists()


def test_compute_confidence_no_metadata_gives_low(vault_path: Path) -> None:
    results = compute_confidence(vault_path, ["API_KEY"])
    assert results["API_KEY"].level == "low"
    assert results["API_KEY"].score == 0


def test_compute_confidence_with_note_increases_score(vault_path: Path) -> None:
    notes_path = vault_path.with_suffix(".notes.json")
    notes_path.write_text(json.dumps({"API_KEY": "important key"}))
    results = compute_confidence(vault_path, ["API_KEY"])
    assert results["API_KEY"].score >= 15
    assert "has note" in results["API_KEY"].reasons


def test_compute_confidence_multiple_signals_accumulate(vault_path: Path) -> None:
    vault_path.with_suffix(".notes.json").write_text(json.dumps({"API_KEY": "note"}))
    vault_path.with_suffix(".tags.json").write_text(json.dumps({"API_KEY": ["prod"]}))
    vault_path.with_suffix(".ownership.json").write_text(json.dumps({"API_KEY": "alice"}))
    results = compute_confidence(vault_path, ["API_KEY"])
    assert results["API_KEY"].score >= 40
    assert results["API_KEY"].level in ("medium", "high")


def test_get_confidence_returns_none_when_missing(vault_path: Path) -> None:
    assert get_confidence(vault_path, "API_KEY") is None


def test_get_confidence_returns_score_after_compute(vault_path: Path) -> None:
    compute_confidence(vault_path, ["API_KEY"])
    result = get_confidence(vault_path, "API_KEY")
    assert result is not None
    assert result.key == "API_KEY"
    assert isinstance(result.score, int)
