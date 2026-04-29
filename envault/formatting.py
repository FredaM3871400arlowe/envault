"""Key value formatting rules for vault entries."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

FORMATS = {"upper", "lower", "title", "strip", "none"}


def _formatting_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".formatting.json")


def load_formatting(vault_path: Path) -> dict:
    p = _formatting_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_formatting(vault_path: Path, data: dict) -> None:
    _formatting_path(vault_path).write_text(json.dumps(data, indent=2))


def set_format(vault_path: Path, key: str, fmt: str) -> None:
    if fmt not in FORMATS:
        raise ValueError(f"Invalid format '{fmt}'. Choose from: {sorted(FORMATS)}")
    data = load_formatting(vault_path)
    data[key] = fmt
    save_formatting(vault_path, data)


def get_format(vault_path: Path, key: str) -> Optional[str]:
    return load_formatting(vault_path).get(key)


def remove_format(vault_path: Path, key: str) -> None:
    data = load_formatting(vault_path)
    data.pop(key, None)
    save_formatting(vault_path, data)


def apply_format(value: str, fmt: str) -> str:
    """Apply a named format rule to a string value."""
    if fmt == "upper":
        return value.upper()
    if fmt == "lower":
        return value.lower()
    if fmt == "title":
        return value.title()
    if fmt == "strip":
        return value.strip()
    return value


def list_formats(vault_path: Path) -> dict:
    """Return all key -> format mappings."""
    return load_formatting(vault_path)
