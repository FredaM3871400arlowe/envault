"""Vault key maturity tracking — classifies keys by age and change frequency."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

MATURITY_LEVELS = ("new", "developing", "stable", "mature", "stale")


def _maturity_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".maturity.json")


def load_maturity(vault_path: Path) -> Dict[str, dict]:
    p = _maturity_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_maturity(vault_path: Path, data: Dict[str, dict]) -> None:
    _maturity_path(vault_path).write_text(json.dumps(data, indent=2))


@dataclass
class MaturityResult:
    key: str
    level: str
    age_days: float
    change_count: int
    last_seen: str


def _classify(age_days: float, change_count: int) -> str:
    if age_days < 1:
        return "new"
    if change_count >= 10 and age_days >= 30:
        return "mature"
    if age_days >= 90 and change_count <= 1:
        return "stale"
    if age_days >= 14:
        return "stable"
    return "developing"


def compute_maturity(
    vault_path: Path,
    keys: List[str],
    history: Optional[Dict[str, List[dict]]] = None,
) -> Dict[str, MaturityResult]:
    """Compute maturity for each key and persist results."""
    now = datetime.now(timezone.utc)
    history = history or {}
    results: Dict[str, MaturityResult] = {}

    for key in keys:
        changes = history.get(key, [])
        change_count = len(changes)
        if changes:
            first_ts = changes[0].get("timestamp", now.isoformat())
            last_ts = changes[-1].get("timestamp", now.isoformat())
            first_dt = datetime.fromisoformat(first_ts)
            age_days = (now - first_dt).total_seconds() / 86400
        else:
            age_days = 0.0
            last_ts = now.isoformat()

        level = _classify(age_days, change_count)
        results[key] = MaturityResult(
            key=key,
            level=level,
            age_days=round(age_days, 2),
            change_count=change_count,
            last_seen=last_ts,
        )

    raw = {
        k: {"level": v.level, "age_days": v.age_days,
            "change_count": v.change_count, "last_seen": v.last_seen}
        for k, v in results.items()
    }
    save_maturity(vault_path, raw)
    return results


def get_maturity(vault_path: Path, key: str) -> Optional[MaturityResult]:
    data = load_maturity(vault_path)
    if key not in data:
        return None
    d = data[key]
    return MaturityResult(key=key, **d)
