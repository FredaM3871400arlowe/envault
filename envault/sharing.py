"""Vault sharing utilities — export an encrypted vault bundle for sharing."""

from __future__ import annotations

import json
import base64
import os
from pathlib import Path
from typing import Optional

from envault.vault import read_vault, create_vault
from envault.crypto import encrypt, decrypt


def export_bundle(
    vault_path: str | Path,
    password: str,
    recipient_password: str,
    output_path: Optional[str | Path] = None,
) -> Path:
    """Re-encrypt vault contents under a recipient password and write a bundle file.

    The bundle is a JSON file containing a base64-encoded ciphertext so it is
    safe to share over plain-text channels (e-mail, Slack, etc.).

    Args:
        vault_path: Path to the source vault.
        password: Password that unlocks the source vault.
        recipient_password: Password the recipient will use to open the bundle.
        output_path: Destination path for the bundle.  Defaults to
            ``<vault_stem>.bundle.json`` next to the vault.

    Returns:
        Path to the written bundle file.
    """
    vault_path = Path(vault_path)
    env_data = read_vault(vault_path, password)

    plaintext = json.dumps(env_data).encode()
    ciphertext: bytes = encrypt(plaintext, recipient_password)

    bundle = {
        "version": 1,
        "source": vault_path.name,
        "payload": base64.b64encode(ciphertext).decode(),
    }

    if output_path is None:
        output_path = vault_path.with_name(vault_path.stem + ".bundle.json")
    output_path = Path(output_path)
    output_path.write_text(json.dumps(bundle, indent=2))
    return output_path


def import_bundle(
    bundle_path: str | Path,
    recipient_password: str,
    vault_path: str | Path,
    vault_password: str,
) -> Path:
    """Decrypt a shared bundle and merge its contents into a vault.

    If *vault_path* does not exist a new vault is created.  Existing keys are
    overwritten; keys not present in the bundle are left untouched.

    Args:
        bundle_path: Path to the ``.bundle.json`` file.
        recipient_password: Password used when the bundle was exported.
        vault_path: Destination vault path.
        vault_password: Password to protect the destination vault.

    Returns:
        Path to the (possibly newly created) vault.
    """
    bundle_path = Path(bundle_path)
    bundle = json.loads(bundle_path.read_text())

    ciphertext = base64.b64decode(bundle["payload"])
    plaintext = decrypt(ciphertext, recipient_password)
    incoming: dict[str, str] = json.loads(plaintext)

    vault_path = Path(vault_path)
    if vault_path.exists():
        existing = read_vault(vault_path, vault_password)
        existing.update(incoming)
        merged = existing
        # Re-create vault with merged data
        vault_path.unlink()
        create_vault(vault_path, vault_password, merged)
    else:
        create_vault(vault_path, vault_password, incoming)

    return vault_path
