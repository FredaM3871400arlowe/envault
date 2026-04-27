"""Constraints: attach validation rules (regex, min/max length, allowed values) to vault keys."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def _constraints_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".constraints.json")


def load_constraints(vault_path: str | Path) -> dict[str, dict[str, Any]]:
    path = _constraints_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_constraints(vault_path: str | Path, data: dict[str, dict[str, Any]]) -> None:
    _constraints_path(vault_path).write_text(json.dumps(data, indent=2))


def set_constraint(
    vault_path: str | Path,
    key: str,
    *,
    pattern: str | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    allowed_values: list[str] | None = None,
) -> dict[str, Any]:
    """Attach a constraint definition to *key*. Returns the stored constraint."""
    if not key:
        raise ValueError("key must not be empty")
    if pattern is not None:
        re.compile(pattern)  # validate regex early
    data = load_constraints(vault_path)
    constraint: dict[str, Any] = {}
    if pattern is not None:
        constraint["pattern"] = pattern
    if min_length is not None:
        constraint["min_length"] = min_length
    if max_length is not None:
        constraint["max_length"] = max_length
    if allowed_values is not None:
        constraint["allowed_values"] = list(allowed_values)
    data[key] = constraint
    save_constraints(vault_path, data)
    return constraint


def get_constraint(vault_path: str | Path, key: str) -> dict[str, Any] | None:
    return load_constraints(vault_path).get(key)


def remove_constraint(vault_path: str | Path, key: str) -> bool:
    data = load_constraints(vault_path)
    if key not in data:
        return False
    del data[key]
    save_constraints(vault_path, data)
    return True


def check_value(constraint: dict[str, Any], value: str) -> list[str]:
    """Return a list of violation messages (empty list means OK)."""
    violations: list[str] = []
    if "pattern" in constraint:
        if not re.fullmatch(constraint["pattern"], value):
            violations.append(f"value does not match pattern '{constraint['pattern']}'")
    if "min_length" in constraint and len(value) < constraint["min_length"]:
        violations.append(
            f"value length {len(value)} is below minimum {constraint['min_length']}"
        )
    if "max_length" in constraint and len(value) > constraint["max_length"]:
        violations.append(
            f"value length {len(value)} exceeds maximum {constraint['max_length']}"
        )
    if "allowed_values" in constraint and value not in constraint["allowed_values"]:
        violations.append(
            f"value '{value}' is not in allowed values {constraint['allowed_values']}"
        )
    return violations
