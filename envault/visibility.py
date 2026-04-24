"""Visibility control for vault keys (public / private / restricted)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

VALID_LEVELS = {"public", "private", "restricted"}


def _visibility_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".visibility.json")


def load_visibility(vault_path: str | Path) -> Dict[str, str]:
    """Return the visibility mapping for a vault, or {} if none exists."""
    path = _visibility_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_visibility(vault_path: str | Path, data: Dict[str, str]) -> None:
    path = _visibility_path(vault_path)
    path.write_text(json.dumps(data, indent=2))


def set_visibility(vault_path: str | Path, key: str, level: str) -> str:
    """Set visibility *level* for *key*.  Returns the level that was stored."""
    if level not in VALID_LEVELS:
        raise ValueError(
            f"Invalid visibility level '{level}'. Choose from: {', '.join(sorted(VALID_LEVELS))}"
        )
    data = load_visibility(vault_path)
    data[key] = level
    save_visibility(vault_path, data)
    return level


def get_visibility(vault_path: str | Path, key: str) -> str | None:
    """Return the visibility level for *key*, or None if not set."""
    return load_visibility(vault_path).get(key)


def remove_visibility(vault_path: str | Path, key: str) -> bool:
    """Remove the visibility entry for *key*.  Returns True if it existed."""
    data = load_visibility(vault_path)
    if key not in data:
        return False
    del data[key]
    save_visibility(vault_path, data)
    return True


def list_by_level(vault_path: str | Path, level: str) -> list[str]:
    """Return all keys that have the given visibility *level*."""
    if level not in VALID_LEVELS:
        raise ValueError(
            f"Invalid visibility level '{level}'. Choose from: {', '.join(sorted(VALID_LEVELS))}"
        )
    return [k for k, v in load_visibility(vault_path).items() if v == level]
