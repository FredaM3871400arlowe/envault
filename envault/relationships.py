"""Track relationships (dependencies/links) between vault keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Set

RELATIONSHIP_TYPES = {"requires", "conflicts", "supersedes", "related"}


def _relationships_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".relationships.json")


def load_relationships(vault_path: Path) -> Dict[str, Dict[str, List[str]]]:
    """Load relationships from disk. Returns {key: {rel_type: [targets]}}."""
    path = _relationships_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_relationships(vault_path: Path, data: Dict[str, Dict[str, List[str]]]) -> None:
    path = _relationships_path(vault_path)
    path.write_text(json.dumps(data, indent=2))


def add_relationship(vault_path: Path, key: str, rel_type: str, target: str) -> None:
    """Add a directional relationship from key -> target of rel_type."""
    if rel_type not in RELATIONSHIP_TYPES:
        raise ValueError(f"Unknown relationship type '{rel_type}'. Choose from: {sorted(RELATIONSHIP_TYPES)}")
    if not key or not target:
        raise ValueError("key and target must be non-empty strings.")
    if key == target:
        raise ValueError("A key cannot have a relationship with itself.")
    data = load_relationships(vault_path)
    data.setdefault(key, {}).setdefault(rel_type, [])
    if target not in data[key][rel_type]:
        data[key][rel_type].append(target)
    save_relationships(vault_path, data)


def remove_relationship(vault_path: Path, key: str, rel_type: str, target: str) -> bool:
    """Remove a specific relationship. Returns True if it existed."""
    data = load_relationships(vault_path)
    targets = data.get(key, {}).get(rel_type, [])
    if target not in targets:
        return False
    targets.remove(target)
    if not targets:
        del data[key][rel_type]
    if not data.get(key):
        data.pop(key, None)
    save_relationships(vault_path, data)
    return True


def get_relationships(vault_path: Path, key: str) -> Dict[str, List[str]]:
    """Return all relationships for a given key."""
    return load_relationships(vault_path).get(key, {})


def list_all_related_keys(vault_path: Path) -> Set[str]:
    """Return every key that has at least one relationship."""
    return set(load_relationships(vault_path).keys())
