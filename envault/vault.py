"""Vault management: create, read, and update encrypted .env vaults."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

from envault.crypto import encrypt, decrypt

VAULT_EXTENSION = ".vault"
METADATA_KEY = "__envault_meta__"


def create_vault(path: str, password: str, env_vars: Dict[str, str]) -> Path:
    """Create a new encrypted vault file from a dict of env vars.

    Args:
        path: Destination file path (will add .vault extension if missing).
        password: Password used to encrypt the vault.
        env_vars: Dictionary of environment variable key-value pairs.

    Returns:
        Path to the created vault file.
    """
    vault_path = _ensure_extension(path)
    payload = json.dumps(env_vars).encode()
    ciphertext = encrypt(password, payload)
    vault_path.write_bytes(ciphertext)
    return vault_path


def read_vault(path: str, password: str) -> Dict[str, str]:
    """Decrypt and return the contents of a vault file.

    Args:
        path: Path to the vault file.
        password: Password used to decrypt the vault.

    Returns:
        Dictionary of environment variable key-value pairs.

    Raises:
        FileNotFoundError: If the vault file does not exist.
        ValueError: If the password is incorrect or the vault is corrupted.
    """
    vault_path = _ensure_extension(path)
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault not found: {vault_path}")
    ciphertext = vault_path.read_bytes()
    plaintext = decrypt(password, ciphertext)
    return json.loads(plaintext.decode())


def update_vault(path: str, password: str, updates: Dict[str, str]) -> Dict[str, str]:
    """Merge updates into an existing vault and re-encrypt it.

    Args:
        path: Path to the vault file.
        password: Password used to encrypt/decrypt the vault.
        updates: Key-value pairs to add or overwrite.

    Returns:
        The full updated dictionary stored in the vault.
    """
    existing = read_vault(path, password)
    existing.update(updates)
    create_vault(path, password, existing)
    return existing


def delete_key(path: str, password: str, key: str) -> Dict[str, str]:
    """Remove a single key from the vault.

    Raises:
        KeyError: If the key does not exist in the vault.
    """
    existing = read_vault(path, password)
    if key not in existing:
        raise KeyError(f"Key '{key}' not found in vault.")
    del existing[key]
    create_vault(path, password, existing)
    return existing


def _ensure_extension(path: str) -> Path:
    p = Path(path)
    if p.suffix != VAULT_EXTENSION:
        p = p.with_suffix(VAULT_EXTENSION)
    return p
