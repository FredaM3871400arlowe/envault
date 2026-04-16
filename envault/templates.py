"""Template management for envault — save and apply env key templates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def _templates_path(base_dir: str | Path) -> Path:
    return Path(base_dir) / ".envault_templates.json"


def load_templates(base_dir: str | Path) -> Dict[str, List[str]]:
    """Return all saved templates as {name: [key, ...]}."""
    p = _templates_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_templates(base_dir: str | Path, templates: Dict[str, List[str]]) -> None:
    p = _templates_path(base_dir)
    p.write_text(json.dumps(templates, indent=2))


def add_template(base_dir: str | Path, name: str, keys: List[str]) -> None:
    """Create or overwrite a template."""
    if not keys:
        raise ValueError("A template must contain at least one key.")
    templates = load_templates(base_dir)
    templates[name] = list(keys)
    save_templates(base_dir, templates)


def remove_template(base_dir: str | Path, name: str) -> None:
    templates = load_templates(base_dir)
    if name not in templates:
        raise KeyError(f"Template '{name}' not found.")
    del templates[name]
    save_templates(base_dir, templates)


def get_template(base_dir: str | Path, name: str) -> List[str]:
    templates = load_templates(base_dir)
    if name not in templates:
        raise KeyError(f"Template '{name}' not found.")
    return templates[name]


def apply_template(vault_data: Dict[str, str], keys: List[str]) -> Dict[str, str]:
    """Return only the keys from vault_data that are listed in the template."""
    return {k: vault_data[k] for k in keys if k in vault_data}
