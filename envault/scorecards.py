"""Scorecards: compute and store a health score for vault keys."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from envault.vault import read_vault
from envault.expiry import load_expiry
from envault.locks import load_locks
from envault.checksums import load_checksums, verify_checksum
from envault.lint import lint_dict


def _scorecards_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(".scorecards.json")


def load_scorecards(vault_path: Path) -> Dict[str, int]:
    p = _scorecards_path(vault_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def save_scorecards(vault_path: Path, data: Dict[str, int]) -> None:
    _scorecards_path(vault_path).write_text(json.dumps(data, indent=2))


@dataclass
class KeyScore:
    key: str
    score: int
    reasons: list[str] = field(default_factory=list)


def _score_key(
    key: str,
    value: str,
    vault_path: Path,
    env: Dict[str, str],
) -> KeyScore:
    """Compute a 0-100 health score for a single key."""
    score = 100
    reasons: list[str] = []

    # Penalty: empty value (-30)
    if not value.strip():
        score -= 30
        reasons.append("empty value")

    # Penalty: placeholder value (-20)
    if value.strip().lower() in ("todo", "fixme", "changeme", "placeholder", "xxx"):
        score -= 20
        reasons.append("placeholder value")

    # Penalty: key naming convention violation (-15)
    report = lint_dict({key: value})
    if not report.ok:
        score -= 15
        reasons.append("naming convention issue")

    # Penalty: expired key (-25)
    expiry = load_expiry(vault_path)
    if key in expiry:
        from datetime import datetime, timezone
        exp = datetime.fromisoformat(expiry[key])
        if exp < datetime.now(timezone.utc):
            score -= 25
            reasons.append("key is expired")

    # Penalty: locked key (-10)
    locks = load_locks(vault_path)
    if locks.get(key):
        score -= 10
        reasons.append("key is locked")

    # Penalty: checksum mismatch (-20)
    checksums = load_checksums(vault_path)
    if key in checksums:
        ok, _ = verify_checksum(vault_path, key, value)
        if not ok:
            score -= 20
            reasons.append("checksum mismatch")

    return KeyScore(key=key, score=max(0, score), reasons=reasons)


def compute_scorecards(vault_path: Path, password: str) -> Dict[str, KeyScore]:
    env = read_vault(vault_path, password)
    results: Dict[str, KeyScore] = {}
    for key, value in env.items():
        results[key] = _score_key(key, value, vault_path, env)
    scores = {k: v.score for k, v in results.items()}
    save_scorecards(vault_path, scores)
    return results


def get_scorecard(vault_path: Path, key: str) -> Optional[int]:
    return load_scorecards(vault_path).get(key)
