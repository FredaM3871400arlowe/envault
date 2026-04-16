"""Tag management for vault keys."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List


def _tags_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".tags.json")


def load_tags(vault_path: str | Path) -> Dict[str, List[str]]:
    path = _tags_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_tags(vault_path: str | Path, tags: Dict[str, List[str]]) -> None:
    _tags_path(vault_path).write_text(json.dumps(tags, indent=2))


def add_tag(vault_path: str | Path, key: str, tag: str) -> None:
    tags = load_tags(vault_path)
    entry = tags.setdefault(key, [])
    if tag not in entry:
        entry.append(tag)
    save_tags(vault_path, tags)


def remove_tag(vault_path: str | Path, key: str, tag: str) -> None:
    tags = load_tags(vault_path)
    if key not in tags or tag not in tags[key]:
        raise KeyError(f"Tag '{tag}' not found on key '{key}'")
    tags[key].remove(tag)
    if not tags[key]:
        del tags[key]
    save_tags(vault_path, tags)


def get_tags(vault_path: str | Path, key: str) -> List[str]:
    return load_tags(vault_path).get(key, [])


def keys_with_tag(vault_path: str | Path, tag: str) -> List[str]:
    return [k for k, v in load_tags(vault_path).items() if tag in v]
