"""Key status aggregation: combines expiry, TTL, locks, and pins into a unified status view."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envault.expiry import load_expiry, get_expiry
from envault.ttl import load_ttl, get_ttl
from envault.locks import load_locks, is_locked
from envault.pins import load_pins, is_pinned


@dataclass
class KeyStatus:
    key: str
    locked: bool = False
    pinned: bool = False
    expiry: Optional[datetime] = None
    ttl_expires: Optional[datetime] = None
    expired: bool = False
    ttl_elapsed: bool = False

    @property
    def healthy(self) -> bool:
        return not self.expired and not self.ttl_elapsed

    def summary(self) -> str:
        parts = []
        if self.locked:
            parts.append("locked")
        if self.pinned:
            parts.append("pinned")
        if self.expired:
            parts.append("expired")
        if self.ttl_elapsed:
            parts.append("ttl-elapsed")
        return ", ".join(parts) if parts else "ok"


def get_key_status(vault_path: Path, key: str) -> KeyStatus:
    """Return a unified status object for a single vault key."""
    now = datetime.now(tz=timezone.utc)

    locked = is_locked(vault_path, key)
    pinned = is_pinned(vault_path, key)

    expiry_dt = get_expiry(vault_path, key)
    ttl_dt = get_ttl(vault_path, key)

    expired = bool(expiry_dt and expiry_dt < now)
    ttl_elapsed = bool(ttl_dt and ttl_dt < now)

    return KeyStatus(
        key=key,
        locked=locked,
        pinned=pinned,
        expiry=expiry_dt,
        ttl_expires=ttl_dt,
        expired=expired,
        ttl_elapsed=ttl_elapsed,
    )


def get_all_statuses(vault_path: Path, keys: list[str]) -> list[KeyStatus]:
    """Return status objects for every key in the provided list."""
    return [get_key_status(vault_path, k) for k in keys]


def format_status(status: KeyStatus) -> str:
    """Return a human-readable single-line status string."""
    flags = []
    if status.locked:
        flags.append("[LOCKED]")
    if status.pinned:
        flags.append("[PINNED]")
    if status.expired:
        flags.append("[EXPIRED]")
    if status.ttl_elapsed:
        flags.append("[TTL-ELAPSED]")
    flag_str = " ".join(flags)
    return f"{status.key}: {flag_str if flag_str else 'ok'}"
