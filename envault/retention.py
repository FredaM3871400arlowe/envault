"""Retention policy management for vault keys."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

VALID_UNITS = ("days", "weeks", "months", "years")


def _retention_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".retention.json")


def load_retention(vault_path: Path) -> dict:
    p = _retention_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_retention(vault_path: Path, data: dict) -> None:
    _retention_path(vault_path).write_text(json.dumps(data, indent=2))


def set_retention(vault_path: Path, key: str, value: int, unit: str) -> datetime:
    """Set a retention policy for *key*. Returns the calculated expiry datetime."""
    if unit not in VALID_UNITS:
        raise ValueError(f"Invalid unit '{unit}'. Must be one of {VALID_UNITS}.")
    if value <= 0:
        raise ValueError("Retention value must be a positive integer.")

    now = datetime.utcnow()
    if unit == "days":
        expires_at = now + timedelta(days=value)
    elif unit == "weeks":
        expires_at = now + timedelta(weeks=value)
    elif unit == "months":
        expires_at = now + timedelta(days=value * 30)
    else:  # years
        expires_at = now + timedelta(days=value * 365)

    data = load_retention(vault_path)
    data[key] = {
        "value": value,
        "unit": unit,
        "set_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
    }
    save_retention(vault_path, data)
    return expires_at


def get_retention(vault_path: Path, key: str) -> Optional[dict]:
    return load_retention(vault_path).get(key)


def remove_retention(vault_path: Path, key: str) -> bool:
    data = load_retention(vault_path)
    if key not in data:
        return False
    del data[key]
    save_retention(vault_path, data)
    return True


def list_expired(vault_path: Path) -> list[str]:
    """Return keys whose retention period has elapsed."""
    now = datetime.utcnow()
    data = load_retention(vault_path)
    return [
        k for k, v in data.items()
        if datetime.fromisoformat(v["expires_at"]) <= now
    ]
