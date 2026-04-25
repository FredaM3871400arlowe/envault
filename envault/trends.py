"""Track and analyse value-change frequency trends for vault keys."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def _trends_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".trends.json")


def load_trends(vault_path: Path) -> Dict[str, List[str]]:
    """Return mapping of key -> list of ISO timestamp strings."""
    p = _trends_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_trends(vault_path: Path, data: Dict[str, List[str]]) -> None:
    _trends_path(vault_path).write_text(json.dumps(data, indent=2))


def record_change(vault_path: Path, key: str) -> str:
    """Record a change event for *key* and return the timestamp."""
    data = load_trends(vault_path)
    ts = datetime.now(timezone.utc).isoformat()
    data.setdefault(key, []).append(ts)
    save_trends(vault_path, data)
    return ts


def get_change_count(vault_path: Path, key: str) -> int:
    """Return how many times *key* has been changed."""
    return len(load_trends(vault_path).get(key, []))


def get_most_changed(vault_path: Path, top_n: int = 5) -> List[tuple]:
    """Return the top-N most frequently changed keys as (key, count) pairs."""
    data = load_trends(vault_path)
    ranked = sorted(data.items(), key=lambda kv: len(kv[1]), reverse=True)
    return [(k, len(v)) for k, v in ranked[:top_n]]


def clear_trends(vault_path: Path, key: str) -> bool:
    """Remove trend history for *key*. Returns True if the key existed."""
    data = load_trends(vault_path)
    if key not in data:
        return False
    del data[key]
    save_trends(vault_path, data)
    return True
