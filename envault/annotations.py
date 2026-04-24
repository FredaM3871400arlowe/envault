"""Per-key annotations: arbitrary freeform metadata strings attached to vault keys."""
from __future__ import annotations

import json
from pathlib import Path

_ANNOTATIONS_FILE = ".envault_annotations.json"


def _annotations_path(vault_path: str | Path) -> Path:
    vault_path = Path(vault_path)
    return vault_path.parent / _ANNOTATIONS_FILE


def load_annotations(vault_path: str | Path) -> dict[str, str]:
    """Return the annotations dict; empty dict if the file does not exist."""
    path = _annotations_path(vault_path)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_annotations(vault_path: str | Path, data: dict[str, str]) -> None:
    """Persist the annotations dict to disk."""
    path = _annotations_path(vault_path)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def set_annotation(vault_path: str | Path, key: str, text: str) -> None:
    """Set (or overwrite) the annotation for *key*."""
    if not key:
        raise ValueError("key must not be empty")
    if not text:
        raise ValueError("annotation text must not be empty")
    data = load_annotations(vault_path)
    data[key] = text
    save_annotations(vault_path, data)


def get_annotation(vault_path: str | Path, key: str) -> str | None:
    """Return the annotation for *key*, or *None* if none is set."""
    return load_annotations(vault_path).get(key)


def remove_annotation(vault_path: str | Path, key: str) -> bool:
    """Remove the annotation for *key*.  Returns True if it existed."""
    data = load_annotations(vault_path)
    if key not in data:
        return False
    del data[key]
    save_annotations(vault_path, data)
    return True


def list_annotations(vault_path: str | Path) -> dict[str, str]:
    """Return all key→annotation mappings."""
    return load_annotations(vault_path)
