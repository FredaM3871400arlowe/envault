"""Password rotation for encrypted vaults."""

from pathlib import Path
from envault.vault import read_vault, create_vault, _ensure_extension
from envault.audit import record_event


def rotate_password(vault_path: str | Path, old_password: str, new_password: str) -> Path:
    """Re-encrypt a vault with a new password.

    Reads the vault with the old password, then writes all key/value pairs
    back using the new password. The original file is overwritten.

    Args:
        vault_path: Path to the vault file.
        old_password: Current password used to decrypt the vault.
        new_password: New password to encrypt the vault with.

    Returns:
        Path to the rotated vault file.

    Raises:
        ValueError: If old_password is incorrect.
        FileNotFoundError: If the vault does not exist.
    """
    vault_path = _ensure_extension(Path(vault_path))

    if not vault_path.exists():
        raise FileNotFoundError(f"Vault not found: {vault_path}")

    # Decrypt with old password — raises ValueError on wrong password
    data = read_vault(vault_path, old_password)

    # Overwrite with new password
    vault_path.unlink()
    create_vault(vault_path, new_password, initial_data=data)

    record_event(vault_path, "rotate", {"keys_count": len(data)})

    return vault_path
