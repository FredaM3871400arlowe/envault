"""Per-key permission flags for envault vaults."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

VALID_PERMISSIONS = {"read", "write", "delete"}


def _permissions_path(vault_path: str | Path) -> Path:
    vault = Path(vault_path)
    return vault.parent / (vault.stem + ".permissions.json")


def load_permissions(vault_path: str | Path) -> Dict[str, List[str]]:
    """Return mapping of key -> list of permissions, or empty dict if missing."""
    p = _permissions_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_permissions(vault_path: str | Path, data: Dict[str, List[str]]) -> None:
    p = _permissions_path(vault_path)
    p.write_text(json.dumps(data, indent=2))


def set_permissions(vault_path: str | Path, key: str, permissions: List[str]) -> None:
    """Set the full permission list for a key, replacing any existing entry."""
    invalid = set(permissions) - VALID_PERMISSIONS
    if invalid:
        raise ValueError(f"Invalid permissions: {invalid}. Must be subset of {VALID_PERMISSIONS}")
    data = load_permissions(vault_path)
    data[key] = sorted(set(permissions))
    save_permissions(vault_path, data)


def get_permissions(vault_path: str | Path, key: str) -> List[str]:
    """Return permissions for a key, or all permissions if no entry exists."""
    data = load_permissions(vault_path)
    return data.get(key, sorted(VALID_PERMISSIONS))


def add_permission(vault_path: str | Path, key: str, permission: str) -> None:
    """Add a single permission to a key's permission set."""
    if permission not in VALID_PERMISSIONS:
        raise ValueError(f"Invalid permission: {permission!r}. Must be one of {VALID_PERMISSIONS}")
    data = load_permissions(vault_path)
    current = set(data.get(key, VALID_PERMISSIONS))
    current.add(permission)
    data[key] = sorted(current)
    save_permissions(vault_path, data)


def remove_permission(vault_path: str | Path, key: str, permission: str) -> None:
    """Remove a single permission from a key's permission set."""
    if permission not in VALID_PERMISSIONS:
        raise ValueError(f"Invalid permission: {permission!r}. Must be one of {VALID_PERMISSIONS}")
    data = load_permissions(vault_path)
    current = set(data.get(key, VALID_PERMISSIONS))
    current.discard(permission)
    data[key] = sorted(current)
    save_permissions(vault_path, data)


def has_permission(vault_path: str | Path, key: str, permission: str) -> bool:
    """Return True if the key has the given permission."""
    return permission in get_permissions(vault_path, key)


def clear_permissions(vault_path: str | Path, key: str) -> None:
    """Remove the permissions entry for a key (reverts to default all-allowed)."""
    data = load_permissions(vault_path)
    data.pop(key, None)
    save_permissions(vault_path, data)
