"""Vault key locking — prevent accidental modification of critical keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List


def _locks_path(vault_path: str | Path) -> Path:
    vault = Path(vault_path)
    return vault.parent / (vault.stem + ".locks.json")


def load_locks(vault_path: str | Path) -> List[str]:
    """Return the list of locked key names for the given vault."""
    path = _locks_path(vault_path)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def save_locks(vault_path: str | Path, locks: List[str]) -> None:
    """Persist the locks list to disk."""
    path = _locks_path(vault_path)
    path.write_text(json.dumps(sorted(set(locks)), indent=2))


def lock_key(vault_path: str | Path, key: str) -> List[str]:
    """Add *key* to the locked set.  Returns the updated list."""
    if not key:
        raise ValueError("Key name must not be empty.")
    locks = load_locks(vault_path)
    if key not in locks:
        locks.append(key)
    save_locks(vault_path, locks)
    return sorted(set(locks))


def unlock_key(vault_path: str | Path, key: str) -> List[str]:
    """Remove *key* from the locked set.  Returns the updated list."""
    locks = load_locks(vault_path)
    if key not in locks:
        raise KeyError(f"Key '{key}' is not locked.")
    locks = [k for k in locks if k != key]
    save_locks(vault_path, locks)
    return sorted(set(locks))


def is_locked(vault_path: str | Path, key: str) -> bool:
    """Return True if *key* is currently locked."""
    return key in load_locks(vault_path)


def assert_not_locked(vault_path: str | Path, key: str) -> None:
    """Raise RuntimeError if *key* is locked."""
    if is_locked(vault_path, key):
        raise RuntimeError(
            f"Key '{key}' is locked and cannot be modified. "
            "Use 'envault locks remove' to unlock it first."
        )
