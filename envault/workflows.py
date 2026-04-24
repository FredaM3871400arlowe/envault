"""Workflow definitions: named sequences of CLI actions applied to a vault."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _workflows_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".workflows.json")


def load_workflows(vault_path: str | Path) -> dict[str, Any]:
    path = _workflows_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_workflows(vault_path: str | Path, data: dict[str, Any]) -> None:
    _workflows_path(vault_path).write_text(json.dumps(data, indent=2))


def add_workflow(
    vault_path: str | Path,
    name: str,
    steps: list[str],
    description: str = "",
) -> None:
    """Register a named workflow with an ordered list of shell step strings."""
    if not name:
        raise ValueError("Workflow name must not be empty.")
    if not steps:
        raise ValueError("Workflow must contain at least one step.")
    data = load_workflows(vault_path)
    data[name] = {"description": description, "steps": steps}
    save_workflows(vault_path, data)


def remove_workflow(vault_path: str | Path, name: str) -> None:
    data = load_workflows(vault_path)
    if name not in data:
        raise KeyError(f"Workflow '{name}' not found.")
    del data[name]
    save_workflows(vault_path, data)


def get_workflow(vault_path: str | Path, name: str) -> dict[str, Any] | None:
    return load_workflows(vault_path).get(name)


def list_workflows(vault_path: str | Path) -> list[str]:
    return sorted(load_workflows(vault_path).keys())
