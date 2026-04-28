"""Sentiment/confidence scoring for vault key values.

Assigns a confidence level to each key based on heuristics such as
value length, presence of special characters, and whether the value
looks like a placeholder or a real secret.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

_PLACEHOLDER_PATTERNS = (
    "changeme",
    "placeholder",
    "todo",
    "fixme",
    "xxx",
    "your_",
    "<",
    ">",
    "example",
)

_CONFIDENCE_LEVELS = ("low", "medium", "high")


def _sentiment_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".sentiment.json")


def load_sentiment(vault_path: Path) -> Dict[str, str]:
    p = _sentiment_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_sentiment(vault_path: Path, data: Dict[str, str]) -> None:
    _sentiment_path(vault_path).write_text(json.dumps(data, indent=2))


@dataclass
class SentimentResult:
    key: str
    value: str
    confidence: str
    reasons: List[str] = field(default_factory=list)


def _score_value(key: str, value: str) -> SentimentResult:
    reasons: List[str] = []
    score = 0

    if len(value) >= 16:
        score += 1
        reasons.append("value length >= 16")
    if any(c in value for c in "!@#$%^&*()-_=+[]{|};:',.<>?/`~"):
        score += 1
        reasons.append("contains special characters")
    lower = value.lower()
    if any(p in lower for p in _PLACEHOLDER_PATTERNS):
        score -= 2
        reasons.append("matches placeholder pattern")
    if not value.strip():
        score -= 2
        reasons.append("empty value")

    if score >= 2:
        confidence = "high"
    elif score == 1:
        confidence = "medium"
    else:
        confidence = "low"

    return SentimentResult(key=key, value=value, confidence=confidence, reasons=reasons)


def analyse_sentiment(vault_path: Path, env: Dict[str, str]) -> Dict[str, SentimentResult]:
    results = {k: _score_value(k, v) for k, v in env.items()}
    save_sentiment(vault_path, {k: r.confidence for k, r in results.items()})
    return results


def get_confidence(vault_path: Path, key: str) -> str | None:
    return load_sentiment(vault_path).get(key)
