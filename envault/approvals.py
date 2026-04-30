"""Approval workflows for sensitive vault key changes."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

APPROVAL_STATES = {"pending", "approved", "rejected"}


def _approvals_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".approvals.json")


def load_approvals(vault_path: Path) -> dict:
    p = _approvals_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_approvals(vault_path: Path, data: dict) -> None:
    _approvals_path(vault_path).write_text(json.dumps(data, indent=2))


def request_approval(vault_path: Path, key: str, requestor: str, reason: str = "") -> dict:
    """Create a pending approval request for a key change."""
    data = load_approvals(vault_path)
    entry = {
        "state": "pending",
        "requestor": requestor,
        "reason": reason,
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "reviewed_by": None,
        "reviewed_at": None,
    }
    data[key] = entry
    save_approvals(vault_path, data)
    return entry


def review_approval(vault_path: Path, key: str, reviewer: str, approve: bool) -> dict:
    """Approve or reject a pending approval request."""
    data = load_approvals(vault_path)
    if key not in data:
        raise KeyError(f"No approval request found for key: {key}")
    entry = data[key]
    if entry["state"] != "pending":
        raise ValueError(f"Approval for '{key}' is already in state '{entry['state']}'")
    entry["state"] = "approved" if approve else "rejected"
    entry["reviewed_by"] = reviewer
    entry["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    save_approvals(vault_path, data)
    return entry


def get_approval(vault_path: Path, key: str) -> Optional[dict]:
    return load_approvals(vault_path).get(key)


def remove_approval(vault_path: Path, key: str) -> None:
    data = load_approvals(vault_path)
    data.pop(key, None)
    save_approvals(vault_path, data)


def list_pending(vault_path: Path) -> dict:
    return {k: v for k, v in load_approvals(vault_path).items() if v["state"] == "pending"}
