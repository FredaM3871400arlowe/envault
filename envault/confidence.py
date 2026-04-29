"""Confidence scoring for vault keys based on metadata richness."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


def _confidence_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".confidence.json")


def load_confidence(vault_path: Path) -> Dict[str, dict]:
    p = _confidence_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_confidence(vault_path: Path, data: Dict[str, dict]) -> None:
    _confidence_path(vault_path).write_text(json.dumps(data, indent=2))


@dataclass
class ConfidenceScore:
    key: str
    score: int          # 0-100
    level: str          # low / medium / high
    reasons: List[str]


_SIGNALS = [
    ("notes",        ".notes.json",        15, "has note"),
    ("tags",         ".tags.json",         10, "has tags"),
    ("labels",       ".labels.json",       10, "has label"),
    ("categories",   ".categories.json",   10, "has category"),
    ("annotations",  ".annotations.json",  15, "has annotation"),
    ("ownership",    ".ownership.json",    15, "has owner"),
    ("constraints",  ".constraints.json",  10, "has constraint"),
    ("schemas",      ".schemas.json",      15, "has schema"),
]


def _level(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def _score_key(vault_path: Path, key: str) -> ConfidenceScore:
    total = 0
    reasons: List[str] = []
    for _name, suffix, points, reason in _signals_for(vault_path):
        p = vault_path.with_suffix(suffix)
        if p.exists():
            try:
                data = json.loads(p.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            if key in data:
                total += points
                reasons.append(reason)
    return ConfidenceScore(key=key, score=min(total, 100), level=_level(total), reasons=reasons)


def _signals_for(vault_path: Path):
    """Yield (name, suffix, points, reason) tuples for existing signal files."""
    for name, suffix, points, reason in _SIGNALS:
        yield name, suffix, points, reason


def compute_confidence(vault_path: Path, keys: List[str]) -> Dict[str, ConfidenceScore]:
    results = {key: _score_key(vault_path, key) for key in keys}
    serialisable = {
        k: {"score": v.score, "level": v.level, "reasons": v.reasons}
        for k, v in results.items()
    }
    save_confidence(vault_path, serialisable)
    return results


def get_confidence(vault_path: Path, key: str) -> ConfidenceScore | None:
    data = load_confidence(vault_path)
    if key not in data:
        return None
    entry = data[key]
    return ConfidenceScore(
        key=key,
        score=entry["score"],
        level=entry["level"],
        reasons=entry["reasons"],
    )
