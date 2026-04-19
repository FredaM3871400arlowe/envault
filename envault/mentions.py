"""Track which vault keys are referenced (mentioned) in source files."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List


def _mentions_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.parent / (p.stem + ".mentions.json")


def load_mentions(vault_path: str | Path) -> Dict[str, List[str]]:
    """Return {key: [file, ...]} mapping."""
    mp = _mentions_path(vault_path)
    if not mp.exists():
        return {}
    return json.loads(mp.read_text())


def save_mentions(vault_path: str | Path, data: Dict[str, List[str]]) -> None:
    _mentions_path(vault_path).write_text(json.dumps(data, indent=2))


def scan_files(
    vault_path: str | Path,
    paths: List[str | Path],
    keys: List[str],
    *,
    overwrite: bool = True,
) -> Dict[str, List[str]]:
    """Scan *paths* for occurrences of each key and persist results."""
    mentions: Dict[str, List[str]] = {} if overwrite else load_mentions(vault_path)

    for key in keys:
        pattern = re.compile(r'\b' + re.escape(key) + r'\b')
        found: List[str] = []
        for fp in paths:
            fp = Path(fp)
            try:
                text = fp.read_text(errors="replace")
            except OSError:
                continue
            if pattern.search(text):
                found.append(str(fp))
        mentions[key] = found

    save_mentions(vault_path, mentions)
    return mentions


def get_mentions(vault_path: str | Path, key: str) -> List[str]:
    """Return list of files that mention *key*."""
    return load_mentions(vault_path).get(key, [])


def clear_mentions(vault_path: str | Path) -> None:
    mp = _mentions_path(vault_path)
    if mp.exists():
        mp.unlink()
