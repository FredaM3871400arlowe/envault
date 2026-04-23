"""Category management for vault keys."""

from __future__ import annotations

import json
from pathlib import Path

VALID_CATEGORIES: set[str] = {
    "auth",
    "database",
    "storage",
    "network",
    "feature",
    "service",
    "logging",
    "misc",
}


def _categories_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".categories.json")


def load_categories(vault_path: str | Path) -> dict[str, str]:
    """Return mapping of key -> category. Empty dict if file missing."""
    path = _categories_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_categories(vault_path: str | Path, data: dict[str, str]) -> None:
    path = _categories_path(vault_path)
    path.write_text(json.dumps(data, indent=2))


def set_category(vault_path: str | Path, key: str, category: str) -> str:
    """Assign *category* to *key*. Returns the category string."""
    if not key:
        raise ValueError("Key must not be empty.")
    if category not in VALID_CATEGORIES:
        raise ValueError(
            f"Invalid category '{category}'. "
            f"Valid options: {sorted(VALID_CATEGORIES)}"
        )
    data = load_categories(vault_path)
    data[key] = category
    save_categories(vault_path, data)
    return category


def get_category(vault_path: str | Path, key: str) -> str | None:
    """Return the category for *key*, or None if unset."""
    return load_categories(vault_path).get(key)


def remove_category(vault_path: str | Path, key: str) -> bool:
    """Remove the category for *key*. Returns True if it existed."""
    data = load_categories(vault_path)
    if key not in data:
        return False
    del data[key]
    save_categories(vault_path, data)
    return True


def list_by_category(vault_path: str | Path, category: str) -> list[str]:
    """Return all keys assigned to *category*."""
    return [
        k for k, v in load_categories(vault_path).items() if v == category
    ]
