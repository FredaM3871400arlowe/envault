"""Namespace support for grouping vault keys under logical prefixes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

NAMESPACES_FILE = ".envault_namespaces.json"


def _namespaces_path(vault_path: Path) -> Path:
    return vault_path.parent / NAMESPACES_FILE


def load_namespaces(vault_path: Path) -> Dict[str, str]:
    """Return mapping of key -> namespace."""
    p = _namespaces_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_namespaces(vault_path: Path, data: Dict[str, str]) -> None:
    _namespaces_path(vault_path).write_text(json.dumps(data, indent=2))


def set_namespace(vault_path: Path, key: str, namespace: str) -> None:
    """Assign *key* to *namespace*."""
    if not namespace.strip():
        raise ValueError("Namespace must not be empty.")
    if not key.strip():
        raise ValueError("Key must not be empty.")
    data = load_namespaces(vault_path)
    data[key] = namespace.strip()
    save_namespaces(vault_path, data)


def get_namespace(vault_path: Path, key: str) -> Optional[str]:
    """Return the namespace for *key*, or None."""
    return load_namespaces(vault_path).get(key)


def remove_namespace(vault_path: Path, key: str) -> None:
    """Remove namespace assignment for *key*."""
    data = load_namespaces(vault_path)
    data.pop(key, None)
    save_namespaces(vault_path, data)


def keys_in_namespace(vault_path: Path, namespace: str) -> List[str]:
    """Return all keys assigned to *namespace*."""
    data = load_namespaces(vault_path)
    return sorted(k for k, ns in data.items() if ns == namespace)


def list_namespaces(vault_path: Path) -> List[str]:
    """Return sorted list of distinct namespace names."""
    data = load_namespaces(vault_path)
    return sorted(set(data.values()))
