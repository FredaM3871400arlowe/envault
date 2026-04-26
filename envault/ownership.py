"""Ownership tracking for vault keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _ownership_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".ownership.json")


def load_ownership(vault_path: Path) -> Dict[str, str]:
    """Load ownership mapping {key: owner} from disk."""
    path = _ownership_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_ownership(vault_path: Path, data: Dict[str, str]) -> None:
    """Persist ownership mapping to disk."""
    _ownership_path(vault_path).write_text(json.dumps(data, indent=2))


def set_owner(vault_path: Path, key: str, owner: str) -> None:
    """Assign an owner to a vault key."""
    if not key:
        raise ValueError("key must not be empty")
    if not owner:
        raise ValueError("owner must not be empty")
    data = load_ownership(vault_path)
    data[key] = owner
    save_ownership(vault_path, data)


def get_owner(vault_path: Path, key: str) -> Optional[str]:
    """Return the owner of a vault key, or None if unset."""
    return load_ownership(vault_path).get(key)


def remove_owner(vault_path: Path, key: str) -> None:
    """Remove ownership metadata for a vault key."""
    data = load_ownership(vault_path)
    data.pop(key, None)
    save_ownership(vault_path, data)


def list_by_owner(vault_path: Path, owner: str) -> List[str]:
    """Return all keys owned by the given owner."""
    data = load_ownership(vault_path)
    return [k for k, v in data.items() if v == owner]
