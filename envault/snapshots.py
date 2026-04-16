"""Snapshot management for envault vaults."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from envault.vault import read_vault


def _snapshots_path(vault_path: str | Path) -> Path:
    vault_path = Path(vault_path)
    return vault_path.parent / (vault_path.stem + ".snapshots.json")


def load_snapshots(vault_path: str | Path) -> list[dict[str, Any]]:
    path = _snapshots_path(vault_path)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def save_snapshots(vault_path: str | Path, snapshots: list[dict[str, Any]]) -> None:
    path = _snapshots_path(vault_path)
    path.write_text(json.dumps(snapshots, indent=2))


def take_snapshot(vault_path: str | Path, password: str, label: str = "") -> dict[str, Any]:
    data = read_vault(vault_path, password)
    snapshot: dict[str, Any] = {
        "timestamp": time.time(),
        "label": label,
        "data": data,
    }
    snapshots = load_snapshots(vault_path)
    snapshots.append(snapshot)
    save_snapshots(vault_path, snapshots)
    return snapshot


def list_snapshots(vault_path: str | Path) -> list[dict[str, Any]]:
    snapshots = load_snapshots(vault_path)
    return [{"index": i, "timestamp": s["timestamp"], "label": s["label"]} for i, s in enumerate(snapshots)]


def restore_snapshot(vault_path: str | Path, password: str, index: int) -> dict[str, str]:
    snapshots = load_snapshots(vault_path)
    if index < 0 or index >= len(snapshots):
        raise IndexError(f"Snapshot index {index} out of range (0-{len(snapshots)-1}).")
    return snapshots[index]["data"]


def delete_snapshot(vault_path: str | Path, index: int) -> None:
    snapshots = load_snapshots(vault_path)
    if index < 0 or index >= len(snapshots):
        raise IndexError(f"Snapshot index {index} out of range.")
    snapshots.pop(index)
    save_snapshots(vault_path, snapshots)
