"""Favorites — mark vault keys as favorites for quick access."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List


def _favorites_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".favorites.json")


def load_favorites(vault_path: str | Path) -> List[str]:
    fp = _favorites_path(vault_path)
    if not fp.exists():
        return []
    return json.loads(fp.read_text())


def save_favorites(vault_path: str | Path, favorites: List[str]) -> None:
    fp = _favorites_path(vault_path)
    fp.write_text(json.dumps(favorites, indent=2))


def add_favorite(vault_path: str | Path, key: str) -> List[str]:
    if not key:
        raise ValueError("Key must not be empty.")
    favs = load_favorites(vault_path)
    if key not in favs:
        favs.append(key)
        save_favorites(vault_path, favs)
    return favs


def remove_favorite(vault_path: str | Path, key: str) -> List[str]:
    favs = load_favorites(vault_path)
    if key not in favs:
        raise KeyError(f"Key '{key}' is not in favorites.")
    favs.remove(key)
    save_favorites(vault_path, favs)
    return favs


def list_favorites(vault_path: str | Path) -> List[str]:
    return load_favorites(vault_path)
