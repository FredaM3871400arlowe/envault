"""Environment management for envault vaults.

Allows keys to be associated with named environments (e.g. dev, staging, prod)
so teams can filter and manage keys per deployment target.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

ENVIRONMENT_FILE = ".envault_environments.json"
VALID_ENVIRONMENTS = {"dev", "staging", "prod", "test", "local"}


def _environments_path(vault_path: Path) -> Path:
    return vault_path.parent / ENVIRONMENT_FILE


def load_environments(vault_path: Path) -> Dict[str, str]:
    """Return mapping of key -> environment name."""
    p = _environments_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_environments(vault_path: Path, data: Dict[str, str]) -> None:
    p = _environments_path(vault_path)
    p.write_text(json.dumps(data, indent=2))


def set_environment(vault_path: Path, key: str, environment: str) -> None:
    """Associate a key with a named environment."""
    if environment not in VALID_ENVIRONMENTS:
        raise ValueError(
            f"Invalid environment '{environment}'. "
            f"Choose from: {', '.join(sorted(VALID_ENVIRONMENTS))}"
        )
    data = load_environments(vault_path)
    data[key] = environment
    save_environments(vault_path, data)


def get_environment(vault_path: Path, key: str) -> Optional[str]:
    """Return the environment for a key, or None if unset."""
    return load_environments(vault_path).get(key)


def remove_environment(vault_path: Path, key: str) -> None:
    """Remove environment association for a key."""
    data = load_environments(vault_path)
    data.pop(key, None)
    save_environments(vault_path, data)


def list_by_environment(vault_path: Path, environment: str) -> List[str]:
    """Return all keys associated with the given environment."""
    data = load_environments(vault_path)
    return sorted(k for k, v in data.items() if v == environment)
