"""Key labelling — attach a human-readable display label to any vault key."""
from __future__ import annotations

import json
from pathlib import Path


def _labels_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".labels.json")


def load_labels(vault_path: str | Path) -> dict[str, str]:
    path = _labels_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_labels(vault_path: str | Path, labels: dict[str, str]) -> None:
    _labels_path(vault_path).write_text(json.dumps(labels, indent=2))


def set_label(vault_path: str | Path, key: str, label: str) -> None:
    if not key:
        raise ValueError("key must not be empty")
    if not label:
        raise ValueError("label must not be empty")
    labels = load_labels(vault_path)
    labels[key] = label
    save_labels(vault_path, labels)


def get_label(vault_path: str | Path, key: str) -> str | None:
    return load_labels(vault_path).get(key)


def remove_label(vault_path: str | Path, key: str) -> None:
    labels = load_labels(vault_path)
    labels.pop(key, None)
    save_labels(vault_path, labels)


def list_labels(vault_path: str | Path) -> dict[str, str]:
    return load_labels(vault_path)
