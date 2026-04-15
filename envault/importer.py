"""Import/export helpers: load a .env file into a vault or export a vault to .env."""

from pathlib import Path
from typing import Dict

from envault.env_parser import parse_env, serialise_env
from envault.vault import create_vault, read_vault


def import_env_file(env_path: str, vault_path: str, password: str) -> Dict[str, str]:
    """Parse a .env file and store its contents in an encrypted vault.

    Args:
        env_path: Path to the source .env file.
        vault_path: Destination vault path (extension added automatically).
        password: Password used to encrypt the vault.

    Returns:
        The dictionary of variables written to the vault.

    Raises:
        FileNotFoundError: If the .env file does not exist.
    """
    source = Path(env_path)
    if not source.exists():
        raise FileNotFoundError(f".env file not found: {env_path}")
    content = source.read_text(encoding="utf-8")
    env_vars = parse_env(content)
    create_vault(vault_path, password, env_vars)
    return env_vars


def export_vault_to_env(vault_path: str, env_path: str, password: str) -> Path:
    """Decrypt a vault and write its contents to a plain .env file.

    Args:
        vault_path: Path to the source vault file.
        env_path: Destination .env file path.
        password: Password used to decrypt the vault.

    Returns:
        Path to the written .env file.

    Raises:
        FileNotFoundError: If the vault file does not exist.
        ValueError: If the password is incorrect.
    """
    env_vars = read_vault(vault_path, password)
    dest = Path(env_path)
    dest.write_text(serialise_env(env_vars), encoding="utf-8")
    return dest


def merge_env_file_into_vault(
    env_path: str, vault_path: str, password: str
) -> Dict[str, str]:
    """Parse a .env file and merge its variables into an existing vault.

    New keys are added; existing keys are overwritten.

    Args:
        env_path: Path to the .env file containing updates.
        vault_path: Path to the target vault.
        password: Vault password.

    Returns:
        The full updated dictionary stored in the vault.
    """
    from envault.vault import update_vault  # local import to avoid circular

    source = Path(env_path)
    if not source.exists():
        raise FileNotFoundError(f".env file not found: {env_path}")
    content = source.read_text(encoding="utf-8")
    updates = parse_env(content)
    return update_vault(vault_path, password, updates)
