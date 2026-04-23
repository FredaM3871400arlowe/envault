"""Checksum tracking for vault keys — detect unexpected external modifications."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _checksums_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".checksums.json")


def load_checksums(vault_path: str | Path) -> dict[str, str]:
    """Return {key: sha256_hex} mapping, or empty dict if file missing."""
    path = _checksums_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_checksums(vault_path: str | Path, data: dict[str, str]) -> None:
    path = _checksums_path(vault_path)
    path.write_text(json.dumps(data, indent=2))


def _hash_value(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def record_checksum(vault_path: str | Path, key: str, value: str) -> str:
    """Store a checksum for *key* and return the hex digest."""
    data = load_checksums(vault_path)
    digest = _hash_value(value)
    data[key] = digest
    save_checksums(vault_path, data)
    return digest


def remove_checksum(vault_path: str | Path, key: str) -> None:
    """Remove the stored checksum for *key* (no-op if absent)."""
    data = load_checksums(vault_path)
    data.pop(key, None)
    save_checksums(vault_path, data)


def verify_checksum(vault_path: str | Path, key: str, value: str) -> bool:
    """Return True if *value* matches the stored checksum for *key*."""
    data = load_checksums(vault_path)
    if key not in data:
        return False
    return data[key] == _hash_value(value)


def verify_all(
    vault_path: str | Path, env: dict[str, str]
) -> dict[str, bool]:
    """Return {key: matches} for every key that has a stored checksum."""
    data = load_checksums(vault_path)
    return {
        key: (_hash_value(env.get(key, "")) == digest)
        for key, digest in data.items()
    }
