"""Track value change history for vault keys."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _history_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".history.json")


def load_history(vault_path: str | Path) -> dict[str, list[dict]]:
    path = _history_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_history(vault_path: str | Path, history: dict[str, list[dict]]) -> None:
    _history_path(vault_path).write_text(json.dumps(history, indent=2))


def record_change(vault_path: str | Path, key: str, old_value: Any, new_value: Any) -> None:
    """Append a change record for *key* to the history log."""
    history = load_history(vault_path)
    history.setdefault(key, []).append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "old": old_value,
            "new": new_value,
        }
    )
    save_history(vault_path, history)


def get_history(vault_path: str | Path, key: str) -> list[dict]:
    """Return the list of change records for *key*, oldest first."""
    return load_history(vault_path).get(key, [])


def clear_history(vault_path: str | Path, key: str | None = None) -> None:
    """Clear history for a single key, or all keys if *key* is None."""
    if key is None:
        save_history(vault_path, {})
    else:
        history = load_history(vault_path)
        history.pop(key, None)
        save_history(vault_path, history)
