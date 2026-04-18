"""Key aliasing — map friendly names to vault keys."""
from __future__ import annotations

import json
from pathlib import Path

_ALIASES_FILE = ".envault-aliases.json"


def _aliases_path(vault_path: str | Path) -> Path:
    return Path(vault_path).with_suffix("").parent / _ALIASES_FILE


def load_aliases(vault_path: str | Path) -> dict[str, str]:
    p = _aliases_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_aliases(vault_path: str | Path, aliases: dict[str, str]) -> None:
    _aliases_path(vault_path).write_text(json.dumps(aliases, indent=2))


def add_alias(vault_path: str | Path, alias: str, key: str) -> None:
    if not alias or not key:
        raise ValueError("alias and key must be non-empty")
    aliases = load_aliases(vault_path)
    aliases[alias] = key
    save_aliases(vault_path, aliases)


def remove_alias(vault_path: str | Path, alias: str) -> None:
    aliases = load_aliases(vault_path)
    if alias not in aliases:
        raise KeyError(f"Alias '{alias}' not found")
    del aliases[alias]
    save_aliases(vault_path, aliases)


def resolve_alias(vault_path: str | Path, alias: str) -> str:
    """Return the vault key for *alias*, or *alias* itself if not mapped."""
    return load_aliases(vault_path).get(alias, alias)


def list_aliases(vault_path: str | Path) -> dict[str, str]:
    return load_aliases(vault_path)
