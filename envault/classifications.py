"""Key classification module for envault.

Assigns semantic classifications to vault keys based on naming patterns
and value characteristics (e.g. secret, config, credential, url).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Optional

CLASSIFICATIONS = [
    "secret",
    "credential",
    "config",
    "url",
    "token",
    "flag",
    "other",
]

_SECRET_PATTERN = re.compile(r"(secret|password|passwd|pwd|private)", re.IGNORECASE)
_CREDENTIAL_PATTERN = re.compile(r"(api_key|apikey|auth|credential|access_key)", re.IGNORECASE)
_URL_PATTERN = re.compile(r"(url|uri|endpoint|host|dsn)", re.IGNORECASE)
_TOKEN_PATTERN = re.compile(r"(token|jwt|bearer|oauth)", re.IGNORECASE)
_FLAG_PATTERN = re.compile(r"(enable|disable|flag|feature|toggle)", re.IGNORECASE)


def _classifications_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".classifications.json")


def load_classifications(vault_path: Path) -> Dict[str, str]:
    p = _classifications_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_classifications(vault_path: Path, data: Dict[str, str]) -> None:
    _classifications_path(vault_path).write_text(json.dumps(data, indent=2))


def classify_key(key: str, value: str = "") -> str:
    """Infer a classification label for a key/value pair."""
    if _SECRET_PATTERN.search(key):
        return "secret"
    if _CREDENTIAL_PATTERN.search(key):
        return "credential"
    if _TOKEN_PATTERN.search(key):
        return "token"
    if _URL_PATTERN.search(key):
        return "url"
    if _FLAG_PATTERN.search(key):
        return "flag"
    # value-based heuristic: looks like a URL
    if value.startswith(("http://", "https://", "postgres://", "redis://")):
        return "url"
    return "other"


def set_classification(vault_path: Path, key: str, classification: str) -> None:
    if classification not in CLASSIFICATIONS:
        raise ValueError(f"Invalid classification '{classification}'. Choose from: {CLASSIFICATIONS}")
    data = load_classifications(vault_path)
    data[key] = classification
    save_classifications(vault_path, data)


def get_classification(vault_path: Path, key: str) -> Optional[str]:
    return load_classifications(vault_path).get(key)


def remove_classification(vault_path: Path, key: str) -> None:
    data = load_classifications(vault_path)
    data.pop(key, None)
    save_classifications(vault_path, data)


def auto_classify(vault_path: Path, env: Dict[str, str]) -> Dict[str, str]:
    """Auto-classify all keys in *env* and persist results."""
    data = load_classifications(vault_path)
    for key, value in env.items():
        if key not in data:
            data[key] = classify_key(key, value)
    save_classifications(vault_path, data)
    return data
