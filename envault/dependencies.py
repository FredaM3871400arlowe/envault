"""Track inter-key dependencies within a vault."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def _deps_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".deps.json")


def load_dependencies(vault_path: str | Path) -> Dict[str, List[str]]:
    """Return mapping of key -> list of keys it depends on."""
    path = _deps_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_dependencies(vault_path: str | Path, deps: Dict[str, List[str]]) -> None:
    _deps_path(vault_path).write_text(json.dumps(deps, indent=2))


def add_dependency(vault_path: str | Path, key: str, depends_on: str) -> None:
    """Record that *key* depends on *depends_on*."""
    if not key:
        raise ValueError("key must not be empty")
    if not depends_on:
        raise ValueError("depends_on must not be empty")
    if key == depends_on:
        raise ValueError("a key cannot depend on itself")
    deps = load_dependencies(vault_path)
    existing = deps.get(key, [])
    if depends_on not in existing:
        existing.append(depends_on)
    deps[key] = existing
    save_dependencies(vault_path, deps)


def remove_dependency(vault_path: str | Path, key: str, depends_on: str) -> None:
    deps = load_dependencies(vault_path)
    if key not in deps or depends_on not in deps[key]:
        raise KeyError(f"dependency {key!r} -> {depends_on!r} not found")
    deps[key].remove(depends_on)
    if not deps[key]:
        del deps[key]
    save_dependencies(vault_path, deps)


def get_dependencies(vault_path: str | Path, key: str) -> List[str]:
    """Return the list of keys that *key* depends on."""
    return load_dependencies(vault_path).get(key, [])


def get_dependents(vault_path: str | Path, key: str) -> List[str]:
    """Return the list of keys that depend on *key*."""
    deps = load_dependencies(vault_path)
    return [k for k, v in deps.items() if key in v]


def clear_dependencies(vault_path: str | Path, key: str) -> None:
    """Remove all dependency records for *key* (both directions)."""
    deps = load_dependencies(vault_path)
    deps.pop(key, None)
    for k in list(deps):
        if key in deps[k]:
            deps[k].remove(key)
            if not deps[k]:
                del deps[k]
    save_dependencies(vault_path, deps)
