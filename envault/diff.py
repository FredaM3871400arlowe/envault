"""Utilities for diffing vault contents against a local .env file."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from envault.env_parser import parse_env
from envault.vault import read_vault


@dataclass
class DiffResult:
    added: List[str]       # keys in vault but not in env file
    removed: List[str]     # keys in env file but not in vault
    changed: List[str]     # keys present in both but with different values
    unchanged: List[str]   # keys present in both with same values

    @property
    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def diff_vault_vs_env(vault_path: str, password: str, env_path: str) -> DiffResult:
    """Compare vault contents with a .env file and return a DiffResult."""
    vault_data: Dict[str, str] = read_vault(vault_path, password)

    with open(env_path, "r", encoding="utf-8") as fh:
        env_data: Dict[str, str] = parse_env(fh.read())

    return diff_dicts(vault_data, env_data)


def diff_dicts(
    vault_data: Dict[str, str], env_data: Dict[str, str]
) -> DiffResult:
    """Pure comparison of two key-value mappings."""
    vault_keys = set(vault_data)
    env_keys = set(env_data)

    added = sorted(vault_keys - env_keys)
    removed = sorted(env_keys - vault_keys)

    changed: List[str] = []
    unchanged: List[str] = []

    for key in sorted(vault_keys & env_keys):
        if vault_data[key] != env_data[key]:
            changed.append(key)
        else:
            unchanged.append(key)

    return DiffResult(added=added, removed=removed, changed=changed, unchanged=unchanged)


def format_diff(result: DiffResult) -> str:
    """Return a human-readable summary of a DiffResult."""
    lines: List[str] = []
    for key in result.added:
        lines.append(f"  + {key}  (in vault, missing from .env)")
    for key in result.removed:
        lines.append(f"  - {key}  (in .env, missing from vault)")
    for key in result.changed:
        lines.append(f"  ~ {key}  (value differs)")
    if not lines:
        return "No differences found."
    return "\n".join(lines)
