"""Priority levels for vault keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

VALID_PRIORITIES = {"low", "medium", "high", "critical"}


def _priorities_path(vault_path: str | Path) -> Path:
    vault_path = Path(vault_path)
    return vault_path.parent / (vault_path.stem + ".priorities.json")


def load_priorities(vault_path: str | Path) -> Dict[str, str]:
    path = _priorities_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_priorities(vault_path: str | Path, data: Dict[str, str]) -> None:
    path = _priorities_path(vault_path)
    path.write_text(json.dumps(data, indent=2))


def set_priority(vault_path: str | Path, key: str, priority: str) -> None:
    """Assign a priority level to a vault key."""
    priority = priority.lower()
    if priority not in VALID_PRIORITIES:
        raise ValueError(
            f"Invalid priority '{priority}'. Must be one of: {sorted(VALID_PRIORITIES)}"
        )
    data = load_priorities(vault_path)
    data[key] = priority
    save_priorities(vault_path, data)


def get_priority(vault_path: str | Path, key: str) -> Optional[str]:
    """Return the priority for *key*, or None if not set."""
    return load_priorities(vault_path).get(key)


def remove_priority(vault_path: str | Path, key: str) -> bool:
    """Remove the priority for *key*. Returns True if it existed."""
    data = load_priorities(vault_path)
    if key not in data:
        return False
    del data[key]
    save_priorities(vault_path, data)
    return True


def list_by_priority(vault_path: str | Path, priority: str) -> list[str]:
    """Return all keys that have the given priority level."""
    priority = priority.lower()
    if priority not in VALID_PRIORITIES:
        raise ValueError(
            f"Invalid priority '{priority}'. Must be one of: {sorted(VALID_PRIORITIES)}"
        )
    data = load_priorities(vault_path)
    return sorted(k for k, v in data.items() if v == priority)
