"""Pre/post command hooks for envault vaults."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import List, Optional

_HOOKS_FILE = ".envault-hooks.json"


def _hooks_path(vault_path: str | Path) -> Path:
    vault_path = Path(vault_path)
    return vault_path.parent / _HOOKS_FILE


def load_hooks(vault_path: str | Path) -> dict:
    path = _hooks_path(vault_path)
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def save_hooks(vault_path: str | Path, hooks: dict) -> None:
    path = _hooks_path(vault_path)
    with path.open("w") as f:
        json.dump(hooks, f, indent=2)


def add_hook(vault_path: str | Path, event: str, command: str) -> None:
    """Register a shell command to run on the given event."""
    valid_events = {"pre-get", "post-get", "pre-set", "post-set", "pre-export", "post-export"}
    if event not in valid_events:
        raise ValueError(f"Unknown event '{event}'. Valid events: {sorted(valid_events)}")
    hooks = load_hooks(vault_path)
    hooks.setdefault(event, [])
    if command not in hooks[event]:
        hooks[event].append(command)
    save_hooks(vault_path, hooks)


def remove_hook(vault_path: str | Path, event: str, command: str) -> None:
    hooks = load_hooks(vault_path)
    cmds: List[str] = hooks.get(event, [])
    if command not in cmds:
        raise KeyError(f"Hook '{command}' not found for event '{event}'")
    cmds.remove(command)
    hooks[event] = cmds
    save_hooks(vault_path, hooks)


def run_hooks(vault_path: str | Path, event: str, env: Optional[dict] = None) -> List[str]:
    """Run all hooks for the given event. Returns list of outputs."""
    hooks = load_hooks(vault_path)
    outputs = []
    for cmd in hooks.get(event, []):
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
        outputs.append(result.stdout.strip())
        if result.returncode != 0:
            raise RuntimeError(f"Hook failed ({cmd}): {result.stderr.strip()}")
    return outputs
