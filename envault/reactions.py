"""Reactions — attach emoji reactions to vault keys."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

VALID_REACTIONS = {"👍", "👎", "❤️", "🔥", "⚠️", "✅", "❌", "🔒", "📌", "🚀"}


def _reactions_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".reactions.json")


def load_reactions(vault_path: Path) -> Dict[str, List[str]]:
    path = _reactions_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_reactions(vault_path: Path, data: Dict[str, List[str]]) -> None:
    _reactions_path(vault_path).write_text(json.dumps(data, indent=2))


def add_reaction(vault_path: Path, key: str, reaction: str) -> List[str]:
    if reaction not in VALID_REACTIONS:
        raise ValueError(
            f"Invalid reaction '{reaction}'. Valid: {sorted(VALID_REACTIONS)}"
        )
    data = load_reactions(vault_path)
    current = data.get(key, [])
    if reaction not in current:
        current.append(reaction)
    data[key] = current
    save_reactions(vault_path, data)
    return current


def remove_reaction(vault_path: Path, key: str, reaction: str) -> List[str]:
    data = load_reactions(vault_path)
    current = data.get(key, [])
    current = [r for r in current if r != reaction]
    if current:
        data[key] = current
    else:
        data.pop(key, None)
    save_reactions(vault_path, data)
    return current


def get_reactions(vault_path: Path, key: str) -> List[str]:
    return load_reactions(vault_path).get(key, [])


def clear_reactions(vault_path: Path, key: str) -> None:
    data = load_reactions(vault_path)
    data.pop(key, None)
    save_reactions(vault_path, data)
