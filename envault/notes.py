"""Per-key notes/comments stored alongside the vault."""
from __future__ import annotations

import json
from pathlib import Path


def _notes_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".notes.json")


def load_notes(vault_path: str | Path) -> dict[str, str]:
    path = _notes_path(vault_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_notes(vault_path: str | Path, notes: dict[str, str]) -> None:
    _notes_path(vault_path).write_text(json.dumps(notes, indent=2))


def set_note(vault_path: str | Path, key: str, note: str) -> None:
    notes = load_notes(vault_path)
    notes[key] = note
    save_notes(vault_path, notes)


def get_note(vault_path: str | Path, key: str) -> str | None:
    return load_notes(vault_path).get(key)


def remove_note(vault_path: str | Path, key: str) -> None:
    notes = load_notes(vault_path)
    if key not in notes:
        raise KeyError(f"No note for key: {key}")
    del notes[key]
    save_notes(vault_path, notes)


def list_notes(vault_path: str | Path) -> dict[str, str]:
    return load_notes(vault_path)
