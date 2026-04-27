"""Threshold management for vault keys.

Allows setting numeric thresholds (min/max) on key values so that
violations can be detected when values are updated.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


THRESHOLDS_FILE = ".envault_thresholds.json"

VALID_KINDS = {"min", "max"}


def _thresholds_path(vault_path: str | Path) -> Path:
    return Path(vault_path).parent / THRESHOLDS_FILE


def load_thresholds(vault_path: str | Path) -> dict:
    path = _thresholds_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_thresholds(vault_path: str | Path, data: dict) -> None:
    _thresholds_path(vault_path).write_text(json.dumps(data, indent=2))


def set_threshold(
    vault_path: str | Path,
    key: str,
    kind: str,
    value: float,
) -> None:
    """Set a min or max threshold for a key."""
    if kind not in VALID_KINDS:
        raise ValueError(f"kind must be one of {VALID_KINDS}, got {kind!r}")
    data = load_thresholds(vault_path)
    entry = data.get(key, {})
    entry[kind] = value
    data[key] = entry
    save_thresholds(vault_path, data)


def get_threshold(vault_path: str | Path, key: str) -> Optional[dict]:
    """Return the threshold dict for *key*, or None if not set."""
    return load_thresholds(vault_path).get(key)


def remove_threshold(vault_path: str | Path, key: str) -> None:
    data = load_thresholds(vault_path)
    data.pop(key, None)
    save_thresholds(vault_path, data)


def check_threshold(vault_path: str | Path, key: str, value: float) -> list[str]:
    """Return a list of violation messages for *value* against stored thresholds."""
    entry = get_threshold(vault_path, key)
    if not entry:
        return []
    violations: list[str] = []
    if "min" in entry and value < entry["min"]:
        violations.append(f"{key}: {value} is below minimum {entry['min']}")
    if "max" in entry and value > entry["max"]:
        violations.append(f"{key}: {value} is above maximum {entry['max']}")
    return violations


def list_thresholds(vault_path: str | Path) -> dict:
    """Return all thresholds keyed by vault key name."""
    return load_thresholds(vault_path)
