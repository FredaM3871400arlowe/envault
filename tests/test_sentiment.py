"""Tests for envault.sentiment."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.sentiment import (
    _sentiment_path,
    _score_value,
    analyse_sentiment,
    get_confidence,
    load_sentiment,
)
from envault.vault import create_vault


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return create_vault(tmp_path / "test.vault", "password", {})


def test_sentiment_path_is_sibling_of_vault(vault_path: Path) -> None:
    p = _sentiment_path(vault_path)
    assert p.parent == vault_path.parent
    assert p.name == "test.sentiment.json"


def test_load_sentiment_returns_empty_when_missing(vault_path: Path) -> None:
    assert load_sentiment(vault_path) == {}


def test_score_value_high_confidence() -> None:
    result = _score_value("SECRET_KEY", "aB3!xQ9#mNpLzR2@")
    assert result.confidence == "high"
    assert result.key == "SECRET_KEY"


def test_score_value_low_confidence_placeholder() -> None:
    result = _score_value("API_KEY", "changeme")
    assert result.confidence == "low"
    assert any("placeholder" in r for r in result.reasons)


def test_score_value_low_confidence_empty() -> None:
    result = _score_value("EMPTY_KEY", "")
    assert result.confidence == "low"
    assert any("empty" in r for r in result.reasons)


def test_score_value_medium_confidence_long_no_special() -> None:
    result = _score_value("DB_PASSWORD", "averylongpasswordwithoutspecials")
    assert result.confidence == "medium"


def test_analyse_sentiment_saves_file(vault_path: Path) -> None:
    env = {"SECRET": "aB3!xQ9#mNpLzR2@", "PLAIN": "changeme"}
    analyse_sentiment(vault_path, env)
    data = load_sentiment(vault_path)
    assert "SECRET" in data
    assert "PLAIN" in data


def test_analyse_sentiment_correct_levels(vault_path: Path) -> None:
    env = {"STRONG": "aB3!xQ9#mNpLzR2@", "WEAK": "changeme"}
    results = analyse_sentiment(vault_path, env)
    assert results["STRONG"].confidence == "high"
    assert results["WEAK"].confidence == "low"


def test_get_confidence_returns_none_when_missing(vault_path: Path) -> None:
    assert get_confidence(vault_path, "MISSING") is None


def test_get_confidence_returns_value_after_analyse(vault_path: Path) -> None:
    env = {"MY_KEY": "aB3!xQ9#mNpLzR2@"}
    analyse_sentiment(vault_path, env)
    confidence = get_confidence(vault_path, "MY_KEY")
    assert confidence == "high"


def test_analyse_empty_vault(vault_path: Path) -> None:
    results = analyse_sentiment(vault_path, {})
    assert results == {}
    assert load_sentiment(vault_path) == {}
