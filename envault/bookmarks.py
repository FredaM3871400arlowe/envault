"""Bookmarks: save named references to frequently accessed vault keys."""
from __future__ import annotations

import json
from pathlib import Path


def _bookmarks_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".bookmarks.json")


def load_bookmarks(vault_path: str | Path) -> dict[str, str]:
    bp = _bookmarks_path(vault_path)
    if not bp.exists():
        return {}
    return json.loads(bp.read_text())


def save_bookmarks(vault_path: str | Path, bookmarks: dict[str, str]) -> None:
    _bookmarks_path(vault_path).write_text(json.dumps(bookmarks, indent=2))


def add_bookmark(vault_path: str | Path, name: str, key: str) -> None:
    if not name:
        raise ValueError("Bookmark name must not be empty.")
    if not key:
        raise ValueError("Key must not be empty.")
    bm = load_bookmarks(vault_path)
    bm[name] = key
    save_bookmarks(vault_path, bm)


def remove_bookmark(vault_path: str | Path, name: str) -> None:
    bm = load_bookmarks(vault_path)
    if name not in bm:
        raise KeyError(f"Bookmark '{name}' not found.")
    del bm[name]
    save_bookmarks(vault_path, bm)


def resolve_bookmark(vault_path: str | Path, name: str) -> str:
    bm = load_bookmarks(vault_path)
    if name not in bm:
        raise KeyError(f"Bookmark '{name}' not found.")
    return bm[name]


def list_bookmarks(vault_path: str | Path) -> dict[str, str]:
    return load_bookmarks(vault_path)
