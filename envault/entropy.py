"""Entropy analysis for vault values — measures randomness/unpredictability."""
from __future__ import annotations

import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from envault.vault import read_vault


def _entropy_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".entropy.json")


def load_entropy(vault_path: Path) -> dict:
    p = _entropy_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_entropy(vault_path: Path, data: dict) -> None:
    _entropy_path(vault_path).write_text(json.dumps(data, indent=2))


@dataclass
class EntropyResult:
    key: str
    value_length: int
    entropy: float
    grade: str  # "high", "medium", "low"


def _calculate_entropy(value: str) -> float:
    """Shannon entropy in bits per character."""
    if not value:
        return 0.0
    counts = Counter(value)
    total = len(value)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def _grade(entropy: float) -> str:
    if entropy >= 3.5:
        return "high"
    if entropy >= 2.0:
        return "medium"
    return "low"


def compute_entropy(vault_path: Path, password: str) -> list[EntropyResult]:
    """Compute entropy for all keys in the vault and persist results."""
    data = read_vault(vault_path, password)
    results: list[EntropyResult] = []
    stored: dict = {}

    for key, value in sorted(data.items()):
        e = _calculate_entropy(value)
        g = _grade(e)
        results.append(EntropyResult(key=key, value_length=len(value), entropy=round(e, 4), grade=g))
        stored[key] = {"value_length": len(value), "entropy": round(e, 4), "grade": g}

    save_entropy(vault_path, stored)
    return results


def get_entropy(vault_path: Path, key: str) -> EntropyResult | None:
    """Return the last computed entropy result for a single key."""
    data = load_entropy(vault_path)
    if key not in data:
        return None
    entry = data[key]
    return EntropyResult(key=key, **entry)


def format_results(results: list[EntropyResult]) -> str:
    lines = [f"{'KEY':<30} {'LEN':>5} {'ENTROPY':>9} {'GRADE'}",
             "-" * 56]
    for r in results:
        lines.append(f"{r.key:<30} {r.value_length:>5} {r.entropy:>9.4f} {r.grade}")
    return "\n".join(lines)
