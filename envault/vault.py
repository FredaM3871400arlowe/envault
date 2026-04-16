"""Vault read/write operations for envault."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envault.crypto import decrypt, encrypt

EXTENSION = ".vault"


def _ensure_extension(path: str | Path) -> Path:
    path = Path(path)
    if path.suffix != EXTENSION:
        path = path.with_suffix(EXTENSION)
    return path


def create_vault(
    path: str | Path,
    password: str,
    initial_data: dict[str, str] | None = None,
) -> Path:
    path = _ensure_extension(path)
    data: dict[str, Any] = initial_data or {}
    plaintext = json.dumps(data).encode()
    ciphertext = encrypt(plaintext, password)
    path.write_bytes(ciphertext)
    return path


def read_vault(path: str | Path, password: str) -> dict[str, str]:
    path = _ensure_extension(path)
    ciphertext = path.read_bytes()
    plaintext = decrypt(ciphertext, password)
    return json.loads(plaintext)


def update_vault(
    path: str | Path,
    password: str,
    updates: dict[str, str],
) -> Path:
    path = _ensure_extension(path)
    data = read_vault(path, password)
    data.update(updates)
    plaintext = json.dumps(data).encode()
    ciphertext = encrypt(plaintext, password)
    path.write_bytes(ciphertext)
    return path


def delete_key(path: str | Path, password: str, key: str) -> Path:
    path = _ensure_extension(path)
    data = read_vault(path, password)
    if key not in data:
        raise KeyError(f"Key '{key}' not found in vault.")
    del data[key]
    plaintext = json.dumps(data).encode()
    ciphertext = encrypt(plaintext, password)
    path.write_bytes(ciphertext)
    return path
