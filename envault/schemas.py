"""Schema validation for vault keys — define and enforce expected types/formats."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

VALID_TYPES = {"string", "integer", "boolean", "url", "email", "uuid"}

_TYPE_PATTERNS: dict[str, re.Pattern[str]] = {
    "integer": re.compile(r"^-?\d+$"),
    "boolean": re.compile(r"^(true|false|1|0)$", re.IGNORECASE),
    "url": re.compile(r"^https?://.+", re.IGNORECASE),
    "email": re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
    "uuid": re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    ),
}


def _schemas_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".schemas.json")


def load_schemas(vault_path: Path) -> dict[str, str]:
    p = _schemas_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_schemas(vault_path: Path, schemas: dict[str, str]) -> None:
    _schemas_path(vault_path).write_text(json.dumps(schemas, indent=2))


def set_schema(vault_path: Path, key: str, type_name: str) -> None:
    if type_name not in VALID_TYPES:
        raise ValueError(
            f"Invalid type '{type_name}'. Choose from: {sorted(VALID_TYPES)}"
        )
    schemas = load_schemas(vault_path)
    schemas[key] = type_name
    save_schemas(vault_path, schemas)


def get_schema(vault_path: Path, key: str) -> str | None:
    return load_schemas(vault_path).get(key)


def remove_schema(vault_path: Path, key: str) -> None:
    schemas = load_schemas(vault_path)
    schemas.pop(key, None)
    save_schemas(vault_path, schemas)


def validate_value(type_name: str, value: str) -> bool:
    """Return True if *value* satisfies *type_name*, False otherwise."""
    if type_name == "string":
        return True
    pattern = _TYPE_PATTERNS.get(type_name)
    return bool(pattern and pattern.match(value))


def validate_vault(vault_path: Path, data: dict[str, Any]) -> list[tuple[str, str, str]]:
    """Validate all keys in *data* against stored schemas.

    Returns a list of (key, expected_type, value) tuples for failing keys.
    """
    schemas = load_schemas(vault_path)
    failures: list[tuple[str, str, str]] = []
    for key, type_name in schemas.items():
        if key not in data:
            continue
        if not validate_value(type_name, str(data[key])):
            failures.append((key, type_name, str(data[key])))
    return failures
