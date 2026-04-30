"""Projections: forecast future vault key counts and change rates based on trend history."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from envault.trends import load_trends


def _projections_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".projections.json")


def load_projections(vault_path: Path) -> Dict[str, dict]:
    p = _projections_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_projections(vault_path: Path, data: Dict[str, dict]) -> None:
    _projections_path(vault_path).write_text(json.dumps(data, indent=2))


@dataclass
class ProjectionResult:
    key: str
    total_changes: int
    avg_changes_per_day: float
    projected_changes_30d: float
    projected_changes_90d: float


def _compute_projection(key: str, entries: List[dict]) -> ProjectionResult:
    """Given a list of trend entries for a key, compute a simple linear projection."""
    if not entries:
        return ProjectionResult(
            key=key,
            total_changes=0,
            avg_changes_per_day=0.0,
            projected_changes_30d=0.0,
            projected_changes_90d=0.0,
        )

    from datetime import datetime, timezone

    timestamps = []
    for e in entries:
        try:
            timestamps.append(datetime.fromisoformat(e["timestamp"]))
        except (KeyError, ValueError):
            pass

    total = len(entries)

    if len(timestamps) >= 2:
        timestamps.sort()
        span_days = max(
            (timestamps[-1] - timestamps[0]).total_seconds() / 86400.0, 1.0
        )
        avg = total / span_days
    else:
        avg = float(total)

    return ProjectionResult(
        key=key,
        total_changes=total,
        avg_changes_per_day=round(avg, 4),
        projected_changes_30d=round(avg * 30, 2),
        projected_changes_90d=round(avg * 90, 2),
    )


def compute_projections(
    vault_path: Path, keys: Optional[List[str]] = None
) -> Dict[str, ProjectionResult]:
    trends = load_trends(vault_path)
    target_keys = keys if keys is not None else list(trends.keys())
    results: Dict[str, ProjectionResult] = {}
    for key in target_keys:
        entries = trends.get(key, [])
        results[key] = _compute_projection(key, entries)
    serialised = {
        k: {
            "total_changes": v.total_changes,
            "avg_changes_per_day": v.avg_changes_per_day,
            "projected_changes_30d": v.projected_changes_30d,
            "projected_changes_90d": v.projected_changes_90d,
        }
        for k, v in results.items()
    }
    save_projections(vault_path, serialised)
    return results
