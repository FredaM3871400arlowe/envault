"""Track and report basic vault usage metrics."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envault.vault import read_vault


def _metrics_path(vault_path: Path) -> Path:
    stem = vault_path.stem
    return vault_path.parent / f"{stem}.metrics.json"


def load_metrics(vault_path: Path) -> Dict:
    p = _metrics_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_metrics(vault_path: Path, data: Dict) -> None:
    _metrics_path(vault_path).write_text(json.dumps(data, indent=2))


@dataclass
class VaultMetrics:
    total_keys: int = 0
    empty_values: int = 0
    avg_value_length: float = 0.0
    key_lengths: List[int] = field(default_factory=list)
    longest_key: str = ""
    shortest_key: str = ""


def compute_metrics(vault_path: Path, password: str) -> VaultMetrics:
    """Read the vault and compute usage metrics."""
    data = read_vault(vault_path, password)
    if not data:
        return VaultMetrics()

    keys = list(data.keys())
    values = list(data.values())

    total_keys = len(keys)
    empty_values = sum(1 for v in values if not v.strip())
    value_lengths = [len(v) for v in values]
    avg_value_length = sum(value_lengths) / total_keys if total_keys else 0.0
    key_lengths = [len(k) for k in keys]
    longest_key = max(keys, key=len) if keys else ""
    shortest_key = min(keys, key=len) if keys else ""

    return VaultMetrics(
        total_keys=total_keys,
        empty_values=empty_values,
        avg_value_length=round(avg_value_length, 2),
        key_lengths=key_lengths,
        longest_key=longest_key,
        shortest_key=shortest_key,
    )


def record_metrics(vault_path: Path, password: str) -> VaultMetrics:
    """Compute and persist metrics for a vault."""
    m = compute_metrics(vault_path, password)
    save_metrics(
        vault_path,
        {
            "total_keys": m.total_keys,
            "empty_values": m.empty_values,
            "avg_value_length": m.avg_value_length,
            "longest_key": m.longest_key,
            "shortest_key": m.shortest_key,
        },
    )
    return m


def format_metrics(m: VaultMetrics) -> str:
    lines = [
        f"Total keys       : {m.total_keys}",
        f"Empty values     : {m.empty_values}",
        f"Avg value length : {m.avg_value_length}",
        f"Longest key      : {m.longest_key or '-'}",
        f"Shortest key     : {m.shortest_key or '-'}",
    ]
    return "\n".join(lines)
