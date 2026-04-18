"""Access control: per-key read/write permissions stored alongside the vault."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Set

PERMISSIONS = ("read", "write")


def _access_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.with_suffix(".access.json")


def load_access(vault_path: str | Path) -> Dict[str, List[str]]:
    """Return mapping of key -> list of allowed permissions."""
    path = _access_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_access(vault_path: str | Path, data: Dict[str, List[str]]) -> None:
    _access_path(vault_path).write_text(json.dumps(data, indent=2))


def grant(vault_path: str | Path, key: str, permission: str) -> None:
    """Grant a permission for a key."""
    if permission not in PERMISSIONS:
        raise ValueError(f"Unknown permission '{permission}'. Choose from {PERMISSIONS}.")
    data = load_access(vault_path)
    perms: Set[str] = set(data.get(key, []))
    perms.add(permission)
    data[key] = sorted(perms)
    save_access(vault_path, data)


def revoke(vault_path: str | Path, key: str, permission: str) -> None:
    """Revoke a permission for a key."""
    data = load_access(vault_path)
    perms: Set[str] = set(data.get(key, []))
    perms.discard(permission)
    if perms:
        data[key] = sorted(perms)
    else:
        data.pop(key, None)
    save_access(vault_path, data)


def check(vault_path: str | Path, key: str, permission: str) -> bool:
    """Return True if the key has the given permission (defaults to allowed if no rules set)."""
    data = load_access(vault_path)
    if key not in data:
        return True  # no restrictions means open
    return permission in data[key]


def list_permissions(vault_path: str | Path, key: str) -> List[str]:
    data = load_access(vault_path)
    return data.get(key, list(PERMISSIONS))
