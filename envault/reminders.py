"""Key-level reminders: schedule a reminder message for a vault key."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

REMINDERS_FILE = ".envault_reminders.json"


def _reminders_path(vault_path: str | Path) -> Path:
    return Path(vault_path).parent / REMINDERS_FILE


def load_reminders(vault_path: str | Path) -> dict:
    p = _reminders_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_reminders(vault_path: str | Path, data: dict) -> None:
    _reminders_path(vault_path).write_text(json.dumps(data, indent=2))


def set_reminder(vault_path: str | Path, key: str, message: str, due: str) -> dict:
    """Set a reminder for *key*. *due* must be an ISO-8601 date string."""
    try:
        due_dt = datetime.fromisoformat(due)
    except ValueError as exc:
        raise ValueError(f"Invalid date format: {due!r}. Use YYYY-MM-DD.") from exc
    data = load_reminders(vault_path)
    data[key] = {"message": message, "due": due_dt.date().isoformat()}
    save_reminders(vault_path, data)
    return data[key]


def get_reminder(vault_path: str | Path, key: str) -> dict | None:
    return load_reminders(vault_path).get(key)


def remove_reminder(vault_path: str | Path, key: str) -> bool:
    data = load_reminders(vault_path)
    if key not in data:
        return False
    del data[key]
    save_reminders(vault_path, data)
    return True


def list_due(vault_path: str | Path, as_of: str | None = None) -> list[dict]:
    """Return reminders whose due date <= *as_of* (defaults to today)."""
    today = datetime.fromisoformat(as_of).date() if as_of else datetime.utcnow().date()
    data = load_reminders(vault_path)
    due = []
    for key, info in data.items():
        if datetime.fromisoformat(info["due"]).date() <= today:
            due.append({"key": key, **info})
    return due
