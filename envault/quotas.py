"""Quota management for vault keys — cap the number of keys per group/namespace."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

DEFAULT_QUOTA = 100
_UNSET = object()


def _quotas_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".quotas.json")


def load_quotas(vault_path: Path) -> dict:
    path = _quotas_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_quotas(vault_path: Path, quotas: dict) -> None:
    _quotas_path(vault_path).write_text(json.dumps(quotas, indent=2))


def set_quota(vault_path: Path, namespace: str, limit: int) -> None:
    """Set the maximum number of keys allowed for a namespace."""
    if limit < 1:
        raise ValueError(f"Quota limit must be a positive integer, got {limit}.")
    quotas = load_quotas(vault_path)
    quotas[namespace] = limit
    save_quotas(vault_path, quotas)


def get_quota(vault_path: Path, namespace: str) -> Optional[int]:
    """Return the quota for *namespace*, or None if not set."""
    return load_quotas(vault_path).get(namespace)


def remove_quota(vault_path: Path, namespace: str) -> None:
    quotas = load_quotas(vault_path)
    quotas.pop(namespace, None)
    save_quotas(vault_path, quotas)


def check_quota(vault_path: Path, namespace: str, current_count: int) -> bool:
    """Return True if *current_count* is within the quota for *namespace*."""
    limit = get_quota(vault_path, namespace)
    if limit is None:
        return True
    return current_count < limit


def list_quotas(vault_path: Path) -> dict:
    """Return all configured quotas as {namespace: limit}."""
    return load_quotas(vault_path)
