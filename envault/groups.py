"""Group keys together under named logical groups."""
from __future__ import annotations

import json
from pathlib import Path


def _groups_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".groups.json")


def load_groups(vault_path: str | Path) -> dict[str, list[str]]:
    path = _groups_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_groups(vault_path: str | Path, data: dict[str, list[str]]) -> None:
    _groups_path(vault_path).write_text(json.dumps(data, indent=2))


def add_to_group(vault_path: str | Path, group: str, key: str) -> None:
    if not group.strip():
        raise ValueError("Group name must not be empty.")
    if not key.strip():
        raise ValueError("Key must not be empty.")
    data = load_groups(vault_path)
    members = data.setdefault(group, [])
    if key not in members:
        members.append(key)
    save_groups(vault_path, data)


def remove_from_group(vault_path: str | Path, group: str, key: str) -> None:
    data = load_groups(vault_path)
    if group not in data:
        raise KeyError(f"Group '{group}' does not exist.")
    if key not in data[group]:
        raise KeyError(f"Key '{key}' is not in group '{group}'.")
    data[group].remove(key)
    if not data[group]:
        del data[group]
    save_groups(vault_path, data)


def delete_group(vault_path: str | Path, group: str) -> None:
    data = load_groups(vault_path)
    if group not in data:
        raise KeyError(f"Group '{group}' does not exist.")
    del data[group]
    save_groups(vault_path, data)


def get_group(vault_path: str | Path, group: str) -> list[str]:
    data = load_groups(vault_path)
    if group not in data:
        raise KeyError(f"Group '{group}' does not exist.")
    return data[group]


def list_groups(vault_path: str | Path) -> list[str]:
    return list(load_groups(vault_path).keys())
