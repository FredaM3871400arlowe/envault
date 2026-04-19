"""Key ratings — let users mark vault keys with a priority/quality rating (1-5)."""
from __future__ import annotations

import json
from pathlib import Path

RATINGS_FILE = ".envault_ratings.json"
_VALID_RATINGS = frozenset(range(1, 6))


def _ratings_path(vault_path: str | Path) -> Path:
    return Path(vault_path).parent / RATINGS_FILE


def load_ratings(vault_path: str | Path) -> dict[str, int]:
    p = _ratings_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_ratings(vault_path: str | Path, ratings: dict[str, int]) -> None:
    _ratings_path(vault_path).write_text(json.dumps(ratings, indent=2))


def set_rating(vault_path: str | Path, key: str, rating: int) -> None:
    if rating not in _VALID_RATINGS:
        raise ValueError(f"Rating must be between 1 and 5, got {rating}")
    ratings = load_ratings(vault_path)
    ratings[key] = rating
    save_ratings(vault_path, ratings)


def get_rating(vault_path: str | Path, key: str) -> int | None:
    return load_ratings(vault_path).get(key)


def remove_rating(vault_path: str | Path, key: str) -> None:
    ratings = load_ratings(vault_path)
    ratings.pop(key, None)
    save_ratings(vault_path, ratings)


def list_ratings(vault_path: str | Path) -> dict[str, int]:
    return load_ratings(vault_path)
