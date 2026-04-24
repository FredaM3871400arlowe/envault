"""Scope management for vault keys — assign keys to named scopes (e.g. dev, staging, prod)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_SCOPES = {"dev", "staging", "prod", "test", "local", "ci"}


def _scopes_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".scopes.json")


def load_scopes(vault_path: Path) -> Dict[str, str]:
    """Return mapping of key -> scope.  Returns empty dict when file is absent."""
    path = _scopes_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_scopes(vault_path: Path, scopes: Dict[str, str]) -> None:
    _scopes_path(vault_path).write_text(json.dumps(scopes, indent=2))


def set_scope(vault_path: Path, key: str, scope: str) -> None:
    """Assign *scope* to *key*.  Raises ValueError for unknown scopes."""
    if scope not in VALID_SCOPES:
        raise ValueError(f"Invalid scope '{scope}'. Must be one of: {sorted(VALID_SCOPES)}")
    scopes = load_scopes(vault_path)
    scopes[key] = scope
    save_scopes(vault_path, scopes)


def get_scope(vault_path: Path, key: str) -> Optional[str]:
    """Return the scope assigned to *key*, or None."""
    return load_scopes(vault_path).get(key)


def remove_scope(vault_path: Path, key: str) -> None:
    """Remove scope assignment for *key* (no-op if absent)."""
    scopes = load_scopes(vault_path)
    scopes.pop(key, None)
    save_scopes(vault_path, scopes)


def keys_in_scope(vault_path: Path, scope: str) -> List[str]:
    """Return all keys assigned to *scope*."""
    return [k for k, s in load_scopes(vault_path).items() if s == scope]
