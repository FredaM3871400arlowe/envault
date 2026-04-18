"""TTL (time-to-live) support for vault keys — auto-expire after a duration."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


def _ttl_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".ttl.json")


def load_ttl(vault_path: str | Path) -> dict:
    path = _ttl_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_ttl(vault_path: str | Path, data: dict) -> None:
    _ttl_path(vault_path).write_text(json.dumps(data, indent=2))


def set_ttl(vault_path: str | Path, key: str, seconds: int) -> datetime:
    """Set a TTL for *key*; returns the computed expiry datetime."""
    if seconds <= 0:
        raise ValueError("TTL must be a positive number of seconds.")
    data = load_ttl(vault_path)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    data[key] = expires_at.isoformat()
    save_ttl(vault_path, data)
    return expires_at


def get_ttl(vault_path: str | Path, key: str) -> Optional[datetime]:
    data = load_ttl(vault_path)
    if key not in data:
        return None
    return datetime.fromisoformat(data[key])


def clear_ttl(vault_path: str | Path, key: str) -> bool:
    data = load_ttl(vault_path)
    if key not in data:
        return False
    del data[key]
    save_ttl(vault_path, data)
    return True


def list_expired(vault_path: str | Path) -> list[str]:
    """Return keys whose TTL has elapsed."""
    data = load_ttl(vault_path)
    now = datetime.now(timezone.utc)
    return [k for k, v in data.items() if datetime.fromisoformat(v) <= now]


def purge_expired(vault_path: str | Path) -> list[str]:
    """Remove expired entries from the TTL store; return purged keys."""
    expired = list_expired(vault_path)
    data = load_ttl(vault_path)
    for k in expired:
        del data[k]
    save_ttl(vault_path, data)
    return expired
