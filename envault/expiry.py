"""Key expiry management for envault vaults."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envault.vault import read_vault, update_vault


def _expiry_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.with_name(p.stem + ".expiry.json")


def load_expiry(vault_path: str | Path) -> dict[str, str]:
    path = _expiry_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_expiry(vault_path: str | Path, data: dict[str, str]) -> None:
    _expiry_path(vault_path).write_text(json.dumps(data, indent=2))


def set_expiry(vault_path: str | Path, key: str, expires_at: datetime) -> None:
    data = load_expiry(vault_path)
    data[key] = expires_at.astimezone(timezone.utc).isoformat()
    save_expiry(vault_path, data)


def clear_expiry(vault_path: str | Path, key: str) -> None:
    data = load_expiry(vault_path)
    data.pop(key, None)
    save_expiry(vault_path, data)


def get_expiry(vault_path: str | Path, key: str) -> Optional[datetime]:
    data = load_expiry(vault_path)
    if key not in data:
        return None
    return datetime.fromisoformat(data[key])


def expired_keys(vault_path: str | Path) -> list[str]:
    data = load_expiry(vault_path)
    now = datetime.now(timezone.utc)
    return [
        k for k, v in data.items()
        if datetime.fromisoformat(v) <= now
    ]


def purge_expired(vault_path: str | Path, password: str) -> list[str]:
    keys = expired_keys(vault_path)
    if not keys:
        return []
    env = read_vault(vault_path, password)
    for k in keys:
        env.pop(k, None)
    update_vault(vault_path, password, env)
    expiry_data = load_expiry(vault_path)
    for k in keys:
        expiry_data.pop(k, None)
    save_expiry(vault_path, expiry_data)
    return keys
