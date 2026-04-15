"""Audit log for tracking vault access and modifications."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_LOG_FILENAME = ".envault_audit.log"


def _audit_log_path(vault_path: str) -> Path:
    """Derive the audit log path from the vault file path."""
    vault = Path(vault_path)
    return vault.parent / AUDIT_LOG_FILENAME


def record_event(
    vault_path: str,
    action: str,
    key: Optional[str] = None,
    actor: Optional[str] = None,
) -> None:
    """Append a structured audit event to the log file.

    Args:
        vault_path: Path to the vault file.
        action: Action performed (e.g. 'init', 'set', 'get', 'delete', 'export', 'import').
        key: The env key involved, if applicable.
        actor: Username or identifier of the actor; defaults to OS user.
    """
    log_path = _audit_log_path(vault_path)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": actor or os.getenv("USER") or os.getenv("USERNAME") or "unknown",
        "vault": str(Path(vault_path).resolve()),
        "action": action,
    }
    if key is not None:
        event["key"] = key

    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")


def read_events(vault_path: str) -> list[dict]:
    """Return all audit events for a vault as a list of dicts."""
    log_path = _audit_log_path(vault_path)
    if not log_path.exists():
        return []
    events = []
    with log_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return events


def clear_events(vault_path: str) -> None:
    """Remove the audit log for a vault."""
    log_path = _audit_log_path(vault_path)
    if log_path.exists():
        log_path.unlink()
