"""Track deprecated keys in a vault — keys that are marked for removal."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Optional


def _deprecations_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".deprecations.json")


def load_deprecations(vault_path: Path) -> dict:
    path = _deprecations_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_deprecations(vault_path: Path, data: dict) -> None:
    _deprecations_path(vault_path).write_text(json.dumps(data, indent=2))


def deprecate_key(
    vault_path: Path,
    key: str,
    reason: str,
    removal_date: Optional[str] = None,
    replacement: Optional[str] = None,
) -> dict:
    """Mark a key as deprecated."""
    if not key:
        raise ValueError("Key must not be empty.")
    if not reason:
        raise ValueError("Reason must not be empty.")
    if removal_date:
        date.fromisoformat(removal_date)  # validate format

    data = load_deprecations(vault_path)
    entry = {
        "reason": reason,
        "deprecated_on": date.today().isoformat(),
    }
    if removal_date:
        entry["removal_date"] = removal_date
    if replacement:
        entry["replacement"] = replacement

    data[key] = entry
    save_deprecations(vault_path, data)
    return entry


def undeprecate_key(vault_path: Path, key: str) -> None:
    """Remove a deprecation record for a key."""
    data = load_deprecations(vault_path)
    if key not in data:
        raise KeyError(f"No deprecation record found for key: {key!r}")
    del data[key]
    save_deprecations(vault_path, data)


def get_deprecation(vault_path: Path, key: str) -> Optional[dict]:
    return load_deprecations(vault_path).get(key)


def list_deprecated(vault_path: Path) -> dict:
    return load_deprecations(vault_path)
