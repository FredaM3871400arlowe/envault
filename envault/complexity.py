"""Vault key value complexity scoring."""
from __future__ import annotations

import json
import re
import string
from pathlib import Path
from typing import NamedTuple

from envault.vault import read_vault


def _complexity_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".complexity.json")


def load_complexity(vault_path: Path) -> dict:
    p = _complexity_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_complexity(vault_path: Path, data: dict) -> None:
    _complexity_path(vault_path).write_text(json.dumps(data, indent=2))


class ComplexityScore(NamedTuple):
    key: str
    score: int          # 0-100
    grade: str          # A-F
    reasons: list[str]


def _score_value(value: str) -> tuple[int, list[str]]:
    """Return (score 0-100, list of reasons for deductions)."""
    if not value:
        return 0, ["empty value"]

    score = 0
    reasons: list[str] = []

    if len(value) >= 8:
        score += 20
    else:
        reasons.append("value shorter than 8 characters")

    if len(value) >= 16:
        score += 10

    if any(c in string.ascii_lowercase for c in value):
        score += 15
    else:
        reasons.append("no lowercase letters")

    if any(c in string.ascii_uppercase for c in value):
        score += 15
    else:
        reasons.append("no uppercase letters")

    if any(c in string.digits for c in value):
        score += 20
    else:
        reasons.append("no digits")

    special = set(string.punctuation)
    if any(c in special for c in value):
        score += 20
    else:
        reasons.append("no special characters")

    if not re.search(r'(.)\1{2,}', value):
        score = min(100, score)
    else:
        score = max(0, score - 10)
        reasons.append("repeated characters detected")

    return min(score, 100), reasons


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def compute_complexity(vault_path: Path, password: str) -> list[ComplexityScore]:
    data = read_vault(vault_path, password)
    results: list[ComplexityScore] = []
    stored: dict[str, dict] = {}

    for key, value in data.items():
        score, reasons = _score_value(value)
        grade = _grade(score)
        results.append(ComplexityScore(key=key, score=score, grade=grade, reasons=reasons))
        stored[key] = {"score": score, "grade": grade, "reasons": reasons}

    save_complexity(vault_path, stored)
    return results


def get_complexity(vault_path: Path, key: str) -> ComplexityScore | None:
    data = load_complexity(vault_path)
    if key not in data:
        return None
    entry = data[key]
    return ComplexityScore(
        key=key,
        score=entry["score"],
        grade=entry["grade"],
        reasons=entry["reasons"],
    )
