"""Profile management for envault — named sets of vault configurations.

Allows users to define multiple profiles (e.g. dev, staging, prod) each
pointing to a different vault file, making it easy to switch contexts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

_PROFILES_FILENAME = ".envault_profiles.json"


def _profiles_path(base_dir: Optional[Path] = None) -> Path:
    """Return path to the profiles config file."""
    root = base_dir or Path.cwd()
    return root / _PROFILES_FILENAME


def load_profiles(base_dir: Optional[Path] = None) -> dict:
    """Load all profiles from disk. Returns empty dict if file missing."""
    path = _profiles_path(base_dir)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_profiles(profiles: dict, base_dir: Optional[Path] = None) -> Path:
    """Persist profiles to disk and return the path written."""
    path = _profiles_path(base_dir)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(profiles, fh, indent=2)
    return path


def add_profile(
    name: str,
    vault_path: str,
    base_dir: Optional[Path] = None,
) -> dict:
    """Add or overwrite a named profile. Returns updated profiles dict."""
    profiles = load_profiles(base_dir)
    profiles[name] = {"vault": str(vault_path)}
    save_profiles(profiles, base_dir)
    return profiles


def remove_profile(name: str, base_dir: Optional[Path] = None) -> dict:
    """Remove a profile by name. Raises KeyError if not found."""
    profiles = load_profiles(base_dir)
    if name not in profiles:
        raise KeyError(f"Profile '{name}' does not exist.")
    del profiles[name]
    save_profiles(profiles, base_dir)
    return profiles


def get_profile(name: str, base_dir: Optional[Path] = None) -> dict:
    """Retrieve a single profile. Raises KeyError if not found."""
    profiles = load_profiles(base_dir)
    if name not in profiles:
        raise KeyError(f"Profile '{name}' does not exist.")
    return profiles[name]


def list_profiles(base_dir: Optional[Path] = None) -> list[str]:
    """Return sorted list of profile names."""
    return sorted(load_profiles(base_dir).keys())
