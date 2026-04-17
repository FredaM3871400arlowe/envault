"""Watch a .env file for changes and sync into the vault automatically."""
from __future__ import annotations

import time
import hashlib
from pathlib import Path
from typing import Callable

from envault.importer import merge_env_file_into_vault


def _file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def watch_env_file(
    env_path: Path,
    vault_path: Path,
    password: str,
    interval: float = 1.0,
    on_sync: Callable[[Path], None] | None = None,
    stop_after: int | None = None,
) -> None:
    """Poll *env_path* and merge changes into *vault_path* when the file changes.

    Parameters
    ----------
    env_path:   Path to the .env file to watch.
    vault_path: Path to the target vault.
    password:   Vault password used for read/write.
    interval:   Polling interval in seconds.
    on_sync:    Optional callback invoked with the vault path after each sync.
    stop_after: Stop automatically after this many sync events (useful for tests).
    """
    env_path = Path(env_path)
    vault_path = Path(vault_path)

    if not env_path.exists():
        raise FileNotFoundError(f".env file not found: {env_path}")

    last_hash = _file_hash(env_path)
    syncs = 0

    while True:
        time.sleep(interval)
        current_hash = _file_hash(env_path)
        if current_hash != last_hash:
            merge_env_file_into_vault(env_path, vault_path, password)
            last_hash = current_hash
            syncs += 1
            if on_sync:
                on_sync(vault_path)
            if stop_after is not None and syncs >= stop_after:
                return
