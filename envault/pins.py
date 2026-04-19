"""Pin management — mark vault keys as pinned to prevent accidental deletion or overwrite."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List


def _pins_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".pins.json")


def load_pins(vault_path: str | Path) -> List[str]:
    path = _pins_path(vault_path)
    if not path.exists():
        return []
    return json.loads(path.read_text())


def save_pins(vault_path: str | Path, pins: List[str]) -> None:
    _pins_path(vault_path).write_text(json.dumps(sorted(set(pins)), indent=2))


def pin_key(vault_path: str | Path, key: str) -> List[str]:
    pins = load_pins(vault_path)
    if key not in pins:
        pins.append(key)
        save_pins(vault_path, pins)
    return load_pins(vault_path)


def unpin_key(vault_path: str | Path, key: str) -> List[str]:
    pins = load_pins(vault_path)
    if key not in pins:
        raise KeyError(f"Key '{key}' is not pinned.")
    pins = [k for k in pins if k != key]
    save_pins(vault_path, pins)
    return pins


def is_pinned(vault_path: str | Path, key: str) -> bool:
    return key in load_pins(vault_path)


def list_pins(vault_path: str | Path) -> List[str]:
    return load_pins(vault_path)
