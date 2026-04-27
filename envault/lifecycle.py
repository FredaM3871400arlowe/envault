"""Lifecycle state management for vault keys.

Supported states: draft, active, deprecated, archived
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

VALID_STATES = {"draft", "active", "deprecated", "archived"}

STATE_TRANSITIONS: Dict[str, set] = {
    "draft":      {"active"},
    "active":     {"deprecated", "archived"},
    "deprecated": {"active", "archived"},
    "archived":   set(),
}


def _lifecycle_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".lifecycle.json")


def load_lifecycle(vault_path: str | Path) -> Dict[str, str]:
    path = _lifecycle_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_lifecycle(vault_path: str | Path, data: Dict[str, str]) -> None:
    _lifecycle_path(vault_path).write_text(json.dumps(data, indent=2))


def set_state(vault_path: str | Path, key: str, state: str) -> str:
    """Set lifecycle state for *key*, respecting valid transition rules."""
    if state not in VALID_STATES:
        raise ValueError(f"Invalid state '{state}'. Choose from: {sorted(VALID_STATES)}")
    data = load_lifecycle(vault_path)
    current = data.get(key, "draft")
    if state != current and state not in STATE_TRANSITIONS.get(current, set()):
        raise ValueError(
            f"Cannot transition '{key}' from '{current}' to '{state}'. "
            f"Allowed: {sorted(STATE_TRANSITIONS.get(current, set())) or 'none'}"
        )
    data[key] = state
    save_lifecycle(vault_path, data)
    return state


def get_state(vault_path: str | Path, key: str) -> Optional[str]:
    return load_lifecycle(vault_path).get(key)


def remove_state(vault_path: str | Path, key: str) -> None:
    data = load_lifecycle(vault_path)
    data.pop(key, None)
    save_lifecycle(vault_path, data)


def list_by_state(vault_path: str | Path, state: str) -> list[str]:
    if state not in VALID_STATES:
        raise ValueError(f"Invalid state '{state}'. Choose from: {sorted(VALID_STATES)}")
    return [k for k, v in load_lifecycle(vault_path).items() if v == state]
