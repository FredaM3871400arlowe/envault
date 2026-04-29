"""Key value signature tracking for envault vaults."""
from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
from typing import Optional


def _signatures_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".signatures.json")


def load_signatures(vault_path: Path) -> dict:
    path = _signatures_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_signatures(vault_path: Path, data: dict) -> None:
    _signatures_path(vault_path).write_text(json.dumps(data, indent=2))


def _sign_value(key: str, value: str, secret: str) -> str:
    """Produce an HMAC-SHA256 hex signature for a key/value pair."""
    payload = f"{key}:{value}".encode()
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def sign_key(vault_path: Path, key: str, value: str, secret: str) -> str:
    """Sign a key/value pair and persist the signature. Returns the signature."""
    sig = _sign_value(key, value, secret)
    data = load_signatures(vault_path)
    data[key] = sig
    save_signatures(vault_path, data)
    return sig


def verify_key(
    vault_path: Path, key: str, value: str, secret: str
) -> bool:
    """Return True if the stored signature matches the current value."""
    data = load_signatures(vault_path)
    if key not in data:
        return False
    expected = _sign_value(key, value, secret)
    return hmac.compare_digest(data[key], expected)


def remove_signature(vault_path: Path, key: str) -> None:
    """Remove the signature entry for a key."""
    data = load_signatures(vault_path)
    data.pop(key, None)
    save_signatures(vault_path, data)


def get_signature(vault_path: Path, key: str) -> Optional[str]:
    """Return the stored signature hex string for a key, or None."""
    return load_signatures(vault_path).get(key)


def list_signed_keys(vault_path: Path) -> list[str]:
    """Return all keys that have a stored signature."""
    return list(load_signatures(vault_path).keys())
